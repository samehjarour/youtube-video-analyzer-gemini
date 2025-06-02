import google.generativeai as genai
import time
import subprocess
import os
import glob
from apify import Actor

async def main():
    async with Actor:
        # Get input from Apify
        actor_input = await Actor.get_input() or {}
        
        # Extract input parameters
        youtube_url = actor_input.get('youtube_url')
        gemini_api_key = actor_input.get('gemini_api_key')
        use_default_key = actor_input.get('use_default_key', False)
        
        # Validate inputs
        if not youtube_url:
            await Actor.fail('YouTube URL is required')
            return
            
        if not use_default_key and not gemini_api_key:
            await Actor.fail('Gemini API key is required when not using default key')
            return
            
        # Use default key if specified, otherwise use provided key
        if use_default_key:
            api_key = "AIzaSyC1xELhT9imEji5TRcVGkSsENhQmsSSo6k"
        else:
            api_key = gemini_api_key
            
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        await Actor.log.info(f"Starting download of YouTube video: {youtube_url}")

        try:
            # Download the video using yt-dlp
            await Actor.log.info("Downloading video...")
            
            # Download with specific format to get a smaller file
            download_command = [
                "yt-dlp", 
                "--format", "best[height<=720]",  # Limit to 720p or lower for smaller file
                "--output", "youtube_video.%(ext)s",
                youtube_url
            ]
            
            result = subprocess.run(download_command, capture_output=True, text=True)
            
            if result.returncode != 0:
                await Actor.fail(f"Download failed: {result.stderr}")
                return
            
            await Actor.log.info("Download successful!")
            
            # Find the downloaded file
            video_files = glob.glob("youtube_video.*")
            if not video_files:
                await Actor.fail("No video file found after download")
                return
            
            video_file_path = video_files[0]
            await Actor.log.info(f"Downloaded file: {video_file_path}")
            
            # Upload the file to Gemini
            await Actor.log.info("Uploading file to Gemini...")
            myfile = genai.upload_file(path=video_file_path)
            await Actor.log.info(f"Upload successful! File ID: {myfile.name}")

            # Wait for file to become active
            await Actor.log.info("Waiting for file to be processed...")
            max_wait_time = 300  # 5 minutes max
            wait_time = 0
            
            while wait_time < max_wait_time:
                file_info = genai.get_file(myfile.name)
                await Actor.log.info(f"File state: {file_info.state.name}")
                
                if file_info.state.name == 'ACTIVE':
                    await Actor.log.info("File is now active and ready!")
                    break
                elif file_info.state.name == 'FAILED':
                    # Clean up downloaded file
                    os.remove(video_file_path)
                    await Actor.fail("File processing failed!")
                    return
                else:
                    await Actor.log.info("Still processing... waiting 15 seconds")
                    time.sleep(15)
                    wait_time += 15
            
            if wait_time >= max_wait_time:
                # Clean up downloaded file
                os.remove(video_file_path)
                await Actor.fail("Timeout waiting for file to be processed.")
                return

            # Generate detailed content analysis
            await Actor.log.info("Generating detailed content analysis...")
            model = genai.GenerativeModel("gemini-2.0-flash")
            
            # First analysis - detailed summary
            await Actor.log.info("Getting detailed summary...")
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
            await Actor.log.info("Extracting key quotes and insights...")
            response2 = model.generate_content([
                myfile,
                """Extract the most important quotes and insights from this video:
                1. List 5-7 key quotes or statements made
                2. Identify the most valuable business advice given
                3. What are the main problems discussed and proposed solutions?
                4. Any specific strategies or frameworks mentioned?"""
            ])
            
            # Third analysis - structure and format
            await Actor.log.info("Analyzing video structure...")
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
            
            await Actor.log.info("Analysis complete! Results saved to dataset.")
            
            # Clean up downloaded file
            await Actor.log.info(f"Cleaning up downloaded file: {video_file_path}")
            os.remove(video_file_path)
            await Actor.log.info("Cleanup complete!")

        except Exception as e:
            await Actor.log.error(f"Error: {e}")
            # Clean up downloaded file if it exists
            video_files = glob.glob("youtube_video.*")
            for file in video_files:
                try:
                    os.remove(file)
                    await Actor.log.info(f"Cleaned up: {file}")
                except:
                    pass
            await Actor.fail(f"Actor failed with error: {e}")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
