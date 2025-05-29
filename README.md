# YouTube Video Analyzer with Gemini AI

This Apify Actor analyzes YouTube videos using Google's Gemini AI to extract comprehensive insights, key quotes, and structural analysis. It downloads videos, processes them with Gemini's multimodal capabilities, and provides detailed analysis.

## Features

- **Comprehensive Video Analysis**: Downloads YouTube videos and analyzes them using Google's Gemini 2.0 Flash model
- **Multi-dimensional Insights**: Provides three types of analysis:
  - Detailed summary with participants, topics, and recommendations
  - Key quotes and business insights extraction
  - Video structure and format analysis
- **Flexible API Key Options**: Use the built-in API key or provide your own
- **Automatic Cleanup**: Downloads videos temporarily and cleans up after processing
- **Quality Optimization**: Downloads videos at 720p or lower to optimize processing time

## Input Parameters

### Required
- **YouTube URL**: The YouTube video URL to analyze (supports both youtu.be and youtube.com formats)

### Optional
- **Use Default Gemini API Key**: Check to use the built-in API key (default: true)
- **Your Gemini API Key**: Provide your own Google Gemini API key if not using the default

## Output

The Actor outputs a structured dataset with the following fields:

```json
{
  "video_url": "https://youtu.be/VIDEO_ID",
  "comprehensive_summary": "Detailed analysis including participants, topics, recommendations...",
  "key_quotes_insights": "Important quotes, business advice, problems and solutions...",
  "video_structure_analysis": "Video type, length, flow, and distinct sections...",
  "file_id": "files/gemini_file_id"
}
```

## Example Use Cases

- **Business Consultation Analysis**: Extract key insights from business meetings or consultations
- **Educational Content Review**: Analyze educational videos for main topics and takeaways
- **Interview Processing**: Extract quotes and insights from interviews
- **Content Strategy**: Understand video structure and messaging for content creation

## How It Works

1. **Download**: Uses yt-dlp to download the YouTube video at optimal quality (720p max)
2. **Upload**: Uploads the video to Google's Gemini AI service
3. **Process**: Waits for Gemini to process the video (up to 5 minutes)
4. **Analyze**: Runs three comprehensive analysis queries:
   - Comprehensive summary analysis
   - Key quotes and insights extraction
   - Video structure analysis
5. **Output**: Saves results to Apify dataset
6. **Cleanup**: Removes temporary video files

## API Key Information

### Using Default Key
The Actor can use a default Gemini API key if configured by the maintainer. The API key is securely stored as an environment variable (`GEMINI_API_KEY`) and never exposed in the code.

**Note**: If you're running this Actor and the default key is not configured, you'll need to provide your own API key.

### Using Your Own Key
To use your own API key:
1. Uncheck "Use Default Gemini API Key"
2. Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
3. Enter your API key in the "Your Gemini API Key" field

### For Developers/Self-Hosting
If you're running this Actor yourself:
1. Set the `GEMINI_API_KEY` environment variable with your API key
2. Or configure it as an Apify secret in your Actor settings

## Technical Requirements

- **Memory**: 4GB (default)
- **Timeout**: 1 hour (default)
- **Dependencies**: 
  - Google Generative AI Python SDK
  - yt-dlp for video downloading
  - ffmpeg for video processing

## Limitations

- Videos must be publicly accessible on YouTube
- Maximum processing time: 5 minutes for Gemini to process the video
- Video quality limited to 720p to optimize processing
- Requires valid Gemini API key (either default or user-provided)

## Error Handling

The Actor includes comprehensive error handling for:
- Invalid YouTube URLs
- Video download failures
- Gemini API errors
- File processing timeouts
- Missing API keys

## Example Input

```json
{
  "youtube_url": "https://youtu.be/u8HpmP8HC-Y",
  "use_default_key": true
}
```

## Example Output

```json
{
  "video_url": "https://youtu.be/u8HpmP8HC-Y",
  "comprehensive_summary": "Here's a detailed analysis of the video:\n\n**1. Detailed Summary...**",
  "key_quotes_insights": "Here are the key details from the video:\n\n1. Key quotes/insights...",
  "video_structure_analysis": "Okay, here is an analysis of the structure and format...",
  "file_id": "files/8jxwwyjs4iqj"
}
```

## Support

For issues or questions about this Actor, please contact the developer or check the Apify documentation.
