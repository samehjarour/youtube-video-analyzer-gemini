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
        youtube_cookies = actor_input.get('youtube_cookies')
        extract_timestamps = actor_input.get('extract_timestamps', True)
        
        # Validate inputs
        if not youtube_url:
            Actor.log.error('YouTube URL is required')
            await Actor.fail()
            return
            
        if not gemini_api_key:
            Actor.log.error('Gemini API key is required')
            await Actor.fail()
            return
            
        # Use the provided API key
        api_key = gemini_api_key
            
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        Actor.log.info(f"Starting download of YouTube video: {youtube_url}")

        try:
            # Download the video using yt-dlp
            Actor.log.info("Downloading video...")
            
            # Prepare cookies file if provided
            cookies_file = None
            if youtube_cookies:
                cookies_file = "cookies.txt"
                with open(cookies_file, "w") as f:
                    f.write(youtube_cookies)
                Actor.log.info("Using provided YouTube cookies")
            
            # Download with specific format to get a smaller file
            download_command = [
                "yt-dlp", 
                "--format", "best[height<=720]",  # Limit to 720p or lower for smaller file
                "--output", "youtube_video.%(ext)s"
            ]
            
            # Add cookies if provided
            if cookies_file:
                download_command.extend(["--cookies", cookies_file])
            
            download_command.append(youtube_url)
            
            result = subprocess.run(download_command, capture_output=True, text=True)
            
            if result.returncode != 0:
                Actor.log.error(f"Download failed: {result.stderr}")
                await Actor.fail()
                return
            
            Actor.log.info("Download successful!")
            
            # Find the downloaded file
            video_files = glob.glob("youtube_video.*")
            if not video_files:
                Actor.log.error("No video file found after download")
                await Actor.fail()
                return
            
            video_file_path = video_files[0]
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
                    Actor.log.error("File processing failed!")
                    await Actor.fail()
                    return
                else:
                    Actor.log.info("Still processing... waiting 15 seconds")
                    time.sleep(15)
                    wait_time += 15
            
            if wait_time >= max_wait_time:
                # Clean up downloaded file
                os.remove(video_file_path)
                Actor.log.error("Timeout waiting for file to be processed.")
                await Actor.fail()
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
            
            # Fourth analysis - timestamp extraction (if enabled)
            timestamps_response = None
            if extract_timestamps:
                Actor.log.info("Extracting important timestamps...")
                timestamps_response = model.generate_content([
                    myfile,
                    """Create a detailed timestamp breakdown of this video. For each important moment, provide:
                    1. Timestamp (in MM:SS or HH:MM:SS format)
                    2. Topic or key point being discussed
                    3. Brief description of what happens at that moment
                    4. Why this moment is significant
                    
                    Focus on:
                    - Key topic transitions
                    - Important insights or advice
                    - Significant quotes or statements
                    - Problem discussions and solutions
                    - Data points or metrics mentioned
                    - Action items or recommendations
                    - Q&A moments (if applicable)
                    
                    Format each timestamp entry like this:
                    [MM:SS] Topic: Description - Significance
                    
                    Provide 10-15 of the most important timestamps throughout the video."""
                ])

            # Prepare the results
            analysis_results = {
                "video_url": youtube_url,
                "comprehensive_summary": response1.text,
                "key_quotes_insights": response2.text,
                "video_structure_analysis": response3.text,
                "file_id": myfile.name,
                "important_timestamps": timestamps_response.text if timestamps_response else None
            }
            
            # Push results to Apify dataset
            await Actor.push_data(analysis_results)
            
            Actor.log.info("Analysis complete! Results saved to dataset.")
            
            # Clean up downloaded file
            Actor.log.info(f"Cleaning up downloaded file: {video_file_path}")
            os.remove(video_file_path)
            
            # Clean up cookies file if it was created
            if cookies_file and os.path.exists(cookies_file):
                os.remove(cookies_file)
                Actor.log.info("Cleaned up cookies file")
            
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
            Actor.log.error(f"Actor failed with error: {e}")
            await Actor.fail()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
