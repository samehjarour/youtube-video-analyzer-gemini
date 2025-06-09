import google.generativeai as genai
import time
import subprocess
import os
import glob
import requests
import boto3
from apify import Actor

async def download_with_external_actor(youtube_url, s3_access_key_id, s3_secret_access_key, s3_bucket, s3_region):
    """Download video using streamers/youtube-video-downloader Actor and retrieve from S3"""
    try:
        # Start the external downloader Actor
        Actor.log.info("Starting external YouTube downloader Actor...")
        
        # Use the MCP tool to run the external Actor
        from apify_client import ApifyClient
        
        # Get Apify token from environment
        apify_token = os.environ.get('APIFY_TOKEN')
        if not apify_token:
            raise Exception("APIFY_TOKEN environment variable is required for external downloader")
        
        client = ApifyClient(apify_token)
        
        # Prepare input for the external Actor
        actor_input = {
            "videos": [{"url": youtube_url}],
            "preferredQuality": "720p",
            "preferredFormat": "mp4",
            "s3AccessKeyId": s3_access_key_id,
            "s3SecretAccessKey": s3_secret_access_key,
            "s3Bucket": s3_bucket,
            "s3Region": s3_region
        }
        
        # Run the Actor
        Actor.log.info("Running streamers/youtube-video-downloader...")
        run = client.actor("streamers/youtube-video-downloader").call(run_input=actor_input)
        
        if run['status'] != 'SUCCEEDED':
            raise Exception(f"External downloader failed with status: {run['status']}")
        
        # Get the results from the Actor run
        dataset_items = list(client.dataset(run['defaultDatasetId']).iterate_items())
        
        if not dataset_items:
            raise Exception("No results from external downloader")
        
        # Extract S3 file information from results
        result = dataset_items[0]
        s3_key = result.get('s3Key') or result.get('fileName')
        
        if not s3_key:
            raise Exception("No S3 key found in downloader results")
        
        # Download the file from S3
        Actor.log.info(f"Downloading video from S3: {s3_key}")
        s3_client = boto3.client(
            's3',
            aws_access_key_id=s3_access_key_id,
            aws_secret_access_key=s3_secret_access_key,
            region_name=s3_region
        )
        
        # Download to local file
        local_filename = "youtube_video.mp4"
        s3_client.download_file(s3_bucket, s3_key, local_filename)
        
        Actor.log.info(f"Successfully downloaded video from S3 to {local_filename}")
        return local_filename
        
    except Exception as e:
        Actor.log.error(f"External downloader failed: {e}")
        return None

async def download_with_ytdlp(youtube_url, cookies):
    """Download video using yt-dlp with fallback strategies"""
    try:
        # Update yt-dlp to latest version to handle YouTube changes
        Actor.log.info("Updating yt-dlp to latest version...")
        update_result = subprocess.run(["yt-dlp", "--update"], capture_output=True, text=True)
        if update_result.returncode == 0:
            Actor.log.info("yt-dlp updated successfully")
        else:
            Actor.log.info("yt-dlp update failed or not needed, continuing with current version")
        
        # Download with specific format to get a smaller file
        # Try multiple strategies to handle YouTube's changing player
        download_strategies = [
            # Strategy 1: Standard download with fallback formats
            [
                "yt-dlp", 
                "--format", "best[height<=720]/best[height<=480]/worst",
                "--output", "youtube_video.%(ext)s",
                "--no-check-certificate",
                "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "--extractor-retries", "5",
                "--fragment-retries", "5",
                "--retry-sleep", "2",
                "--ignore-errors",
                youtube_url
            ],
            # Strategy 2: Force generic extractor if YouTube extractor fails
            [
                "yt-dlp",
                "--force-generic-extractor",
                "--format", "best[height<=720]/best",
                "--output", "youtube_video.%(ext)s",
                "--no-check-certificate",
                "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                youtube_url
            ],
            # Strategy 3: Use audio-only as last resort
            [
                "yt-dlp",
                "--format", "bestaudio/best",
                "--output", "youtube_video.%(ext)s",
                "--no-check-certificate",
                "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                youtube_url
            ]
        ]
        
        # Try each download strategy until one succeeds
        result = None
        cookies_file = None
        
        for strategy_num, download_command in enumerate(download_strategies, 1):
            Actor.log.info(f"Trying download strategy {strategy_num}...")
            
            # Add cookies if provided
            if cookies:
                if not cookies_file:
                    cookies_file = "cookies.txt"
                    with open(cookies_file, 'w') as f:
                        f.write(cookies)
                # Insert cookies at the beginning of the command (after yt-dlp)
                cmd_with_cookies = download_command.copy()
                cmd_with_cookies.insert(1, "--cookies")
                cmd_with_cookies.insert(2, cookies_file)
                download_command = cmd_with_cookies
            
            result = subprocess.run(download_command, capture_output=True, text=True)
            
            if result.returncode == 0:
                Actor.log.info(f"Download successful with strategy {strategy_num}!")
                break
            else:
                Actor.log.warning(f"Strategy {strategy_num} failed: {result.stderr[:200]}...")
                if strategy_num < len(download_strategies):
                    Actor.log.info(f"Trying next strategy...")
                else:
                    Actor.log.error("All download strategies failed")
        
        # Clean up cookies file if it was created
        if cookies_file and os.path.exists(cookies_file):
            os.remove(cookies_file)
            Actor.log.info("Cleaned up cookies file")
        
        if result.returncode != 0:
            Actor.log.error(f"All download strategies failed. Last error: {result.stderr}")
            return None
        
        # Find the downloaded file
        video_files = glob.glob("youtube_video.*")
        if not video_files:
            Actor.log.error("No video file found after download")
            return None
        
        return video_files[0]
        
    except Exception as e:
        Actor.log.error(f"yt-dlp download failed: {e}")
        return None

async def main():
    async with Actor:
        # Get input from Apify
        actor_input = await Actor.get_input() or {}
        
        # Extract input parameters
        youtube_url = actor_input.get('youtube_url')
        gemini_api_key = actor_input.get('gemini_api_key')
        use_default_key = actor_input.get('use_default_key', False)
        cookies = actor_input.get('cookies')
        use_external_downloader = actor_input.get('use_external_downloader', False)
        s3_access_key_id = actor_input.get('s3_access_key_id')
        s3_secret_access_key = actor_input.get('s3_secret_access_key')
        s3_bucket = actor_input.get('s3_bucket')
        s3_region = actor_input.get('s3_region', 'us-east-1')
        
        # Validate inputs
        if not youtube_url:
            await Actor.fail(status_message=f'YouTube URL is required')
            return
            
        if not use_default_key and not gemini_api_key:
            await Actor.fail(status_message=f'Gemini API key is required when not using default key')
            return
            
        # Validate external downloader inputs
        if use_external_downloader:
            if not all([s3_access_key_id, s3_secret_access_key, s3_bucket]):
                await Actor.fail(status_message=f'S3 credentials (access key, secret key, and bucket) are required when using external downloader')
                return
            
        # Use default key if specified, otherwise use provided key
        if use_default_key:
            api_key = "AIzaSyC1xELhT9imEji5TRcVGkSsENhQmsSSo6k"
        else:
            api_key = gemini_api_key
            
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        Actor.log.info(f"Starting download of YouTube video: {youtube_url}")

        try:
            video_file_path = None
            
            if use_external_downloader:
                # Use external YouTube downloader Actor
                Actor.log.info("Using external YouTube downloader Actor...")
                video_file_path = await download_with_external_actor(youtube_url, s3_access_key_id, s3_secret_access_key, s3_bucket, s3_region)
            else:
                # Use yt-dlp with fallback strategies
                Actor.log.info("Using yt-dlp downloader...")
                video_file_path = await download_with_ytdlp(youtube_url, cookies)
            
            if not video_file_path:
                await Actor.fail(status_message=f"Failed to download video")
                return
            
            Actor.log.info(f"Downloaded file: {video_file_path}")
            
            # Upload the file to Gemini
            Actor.log.info("Uploading file to Gemini...")
            myfile = genai.upload_file(path=video_file_path)
            Actor.log.info(f"Upload successful! File ID: {myfile.name}")

            # Wait for file to become active
            Actor.log.info("Waiting for file to be processed...")
            max_wait_time = 300  # 5 minutes max
            wait_time = 0
            
            while wait_time < max_wait_time:
                file_info = genai.get_file(myfile.name)
                Actor.log.info(f"File state: {file_info.state.name}")
                
                if file_info.state.name == 'ACTIVE':
                    Actor.log.info("File is now active and ready!")
                    break
                elif file_info.state.name == 'FAILED':
                    # Clean up downloaded file
                    os.remove(video_file_path)
                    await Actor.fail(status_message=f"File processing failed!")
                    return
                else:
                    Actor.log.info("Still processing... waiting 15 seconds")
                    time.sleep(15)
                    wait_time += 15
            
            if wait_time >= max_wait_time:
                # Clean up downloaded file
                os.remove(video_file_path)
                await Actor.fail(status_message=f"Timeout waiting for file to be processed.")
                return

            # Generate detailed content analysis
            Actor.log.info("Generating detailed content analysis...")
            model = genai.GenerativeModel("gemini-2.0-flash")
            
            # First analysis - detailed summary
            Actor.log.info("Getting detailed summary...")
            response1 = model.generate_content([
                myfile, 
                """Provide a comprehensive analysis of this video including:
                1. Detailed summary of the main content and discussion
                2. Key participants and their roles
                3. Main topics, themes, and advice given
                4. Specific recommendations or actionable insights mentioned
                5. Any data points, numbers, or metrics discussed
                6. Overall tone and style of the conversation"""
            ])
            
            # Second analysis - key quotes and insights
            Actor.log.info("Extracting key quotes and insights...")
            response2 = model.generate_content([
                myfile,
                """Extract the most important quotes and insights from this video:
                1. List 5-7 key quotes or statements made
                2. Identify the most valuable business advice given
                3. What are the main problems discussed and proposed solutions?
                4. Any specific strategies or frameworks mentioned?"""
            ])
            
            # Third analysis - structure and format
            Actor.log.info("Analyzing video structure...")
            response3 = model.generate_content([
                myfile,
                """Analyze the structure and format of this video:
                1. What type of video is this? (interview, presentation, consultation, etc.)
                2. How long is the video approximately?
                3. What is the overall flow and organization of the content?
                4. Are there distinct sections or topics covered?"""
            ])

            # Prepare the results
            analysis_results = {
                "video_url": youtube_url,
                "comprehensive_summary": response1.text,
                "key_quotes_insights": response2.text,
                "video_structure_analysis": response3.text,
                "file_id": myfile.name
            }
            
            # Push results to Apify dataset
            await Actor.push_data(analysis_results)
            
            Actor.log.info("Analysis complete! Results saved to dataset.")
            
            # Clean up downloaded file
            Actor.log.info(f"Cleaning up downloaded file: {video_file_path}")
            os.remove(video_file_path)
            Actor.log.info("Cleanup complete!")

        except Exception as e:
            Actor.log.error(f"Error: {e}")
            # Clean up downloaded file if it exists
            video_files = glob.glob("youtube_video.*")
            for file in video_files:
                try:
                    os.remove(file)
                    Actor.log.info(f"Cleaned up: {file}")
                except:
                    pass
            # Clean up cookies file if it exists
            if os.path.exists("cookies.txt"):
                try:
                    os.remove("cookies.txt")
                    Actor.log.info("Cleaned up cookies file")
                except:
                    pass
            await Actor.fail(status_message=f"Actor failed with error: {e}")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
