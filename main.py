import google.generativeai as genai
from apify import Actor

async def main():
    async with Actor:
        # Get input from Apify
        actor_input = await Actor.get_input() or {}
        
        # Extract input parameters
        youtube_url = actor_input.get('youtube_url')
        gemini_api_key = actor_input.get('gemini_api_key')
        use_default_key = actor_input.get('use_default_key', False)
        num_timestamps = actor_input.get('num_timestamps', 5)
        custom_prompt = actor_input.get('custom_prompt', '').strip()
        
        # Validate inputs
        if not youtube_url:
            await Actor.fail(status_message=f'YouTube URL is required')
            return
            
        if not use_default_key and not gemini_api_key:
            await Actor.fail(status_message=f'Gemini API key is required when not using default key')
            return
            
        # Use default key if specified, otherwise use provided key
        if use_default_key:
            api_key = "AIzaSyC1xELhT9imEji5TRcVGkSsENhQmsSSo6k"
        else:
            api_key = gemini_api_key
            
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        Actor.log.info(f"Starting analysis of YouTube video: {youtube_url}")

        try:
            # Generate detailed content analysis using direct YouTube URL
            Actor.log.info("Generating detailed content analysis using direct YouTube URL...")
            model = genai.GenerativeModel("gemini-2.0-flash")
            
            # Create file data part with YouTube URL
            youtube_file_part = {
                "file_data": {
                    "file_uri": youtube_url
                }
            }
            
            # First analysis - detailed summary
            Actor.log.info("Getting detailed summary...")
            response1 = model.generate_content([
                youtube_file_part,
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
                youtube_file_part,
                """Extract the most important quotes and insights from this video:
                1. List 5-7 key quotes or statements made
                2. Identify the most valuable business advice given
                3. What are the main problems discussed and proposed solutions?
                4. Any specific strategies or frameworks mentioned?"""
            ])
            
            # Third analysis - structure and format
            Actor.log.info("Analyzing video structure...")
            response3 = model.generate_content([
                youtube_file_part,
                """Analyze the structure and format of this video:
                1. What type of video is this? (interview, presentation, consultation, etc.)
                2. How long is the video approximately?
                3. What is the overall flow and organization of the content?
                4. Are there distinct sections or topics covered?"""
            ])

            # Fourth analysis - comprehensive timestamps (if requested)
            timestamps_analysis = None
            if num_timestamps > 0:
                Actor.log.info(f"Extracting {num_timestamps} comprehensive timestamps...")
                response4 = model.generate_content([
                    youtube_file_part,
                    f"""Analyze this video comprehensively and identify the {num_timestamps} most important timestamps that span the entire video duration. 

                    IMPORTANT: Make sure to cover the ENTIRE video from beginning to end, not just the first few minutes. 

                    For each timestamp, provide:
                    1. The exact time (in MM:SS or HH:MM:SS format for longer videos)
                    2. A descriptive title of what happens at that moment
                    3. Detailed explanation of why this moment is significant
                    4. Key quotes or insights from that section (if any)

                    Ensure timestamps are distributed throughout the video:
                    - Include moments from the beginning, middle, and end of the video
                    - Cover major topic transitions and section changes
                    - Highlight the most valuable insights and actionable advice
                    - Include important conclusions and takeaways
                    - Note any significant data points, examples, or case studies mentioned

                    Format your response as:
                    1. [TIMESTAMP] - "Section Title" 
                       Description: [Detailed explanation of what happens and why it's important]
                       Key Points: [Bullet points of main insights from this section]

                    Make sure to watch the ENTIRE video and provide timestamps that represent the full content, not just the opening segments."""
                ])
                timestamps_analysis = response4.text

            # Fifth analysis - custom prompt (if provided)
            custom_analysis = None
            if custom_prompt:
                Actor.log.info("Processing custom prompt...")
                response5 = model.generate_content([
                    youtube_file_part,
                    f"""Based on this video content, please answer the following custom question or prompt:

                    {custom_prompt}

                    Provide a detailed and comprehensive response based on the video content. Include specific examples, quotes, and references to moments in the video when relevant. If the video doesn't contain information to fully answer the question, please indicate what aspects are covered and what might be missing."""
                ])
                custom_analysis = response5.text

            # Prepare the results
            analysis_results = {
                "video_url": youtube_url,
                "comprehensive_summary": response1.text,
                "key_quotes_insights": response2.text,
                "video_structure_analysis": response3.text,
                "processing_method": "direct_youtube_url"
            }
            
            # Add timestamps if extracted
            if timestamps_analysis:
                analysis_results["important_timestamps"] = timestamps_analysis
                analysis_results["num_timestamps_requested"] = num_timestamps
            
            # Add custom analysis if provided
            if custom_analysis:
                analysis_results["custom_analysis"] = custom_analysis
                analysis_results["custom_prompt_used"] = custom_prompt
            
            # Push results to Apify dataset
            await Actor.push_data(analysis_results)
            
            Actor.log.info("Analysis complete! Results saved to dataset.")

        except Exception as e:
            Actor.log.error(f"Error: {e}")
            await Actor.fail(status_message=f"Actor failed with error: {e}")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
