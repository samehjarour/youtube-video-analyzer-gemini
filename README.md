# YouTube Video Analyzer with Gemini AI

This Apify Actor analyzes YouTube videos using Google's Gemini AI to extract comprehensive insights, key quotes, and structural analysis. It downloads videos, processes them with Gemini's multimodal capabilities, and provides detailed analysis.

## Features

- **Comprehensive Video Analysis**: Downloads YouTube videos and analyzes them using Google's Gemini 2.0 Flash model
- **Multi-dimensional Insights**: Provides comprehensive analysis including:
  - Detailed summary with participants, topics, and recommendations
  - Key quotes and business insights extraction
  - Video structure and format analysis
  - **Important timestamps** of key moments and topic transitions
- **Flexible API Key Options**: Use the built-in API key or provide your own
- **Automatic Cleanup**: Downloads videos temporarily and cleans up after processing
- **Quality Optimization**: Downloads videos at 720p or lower to optimize processing time

## Input Parameters

### Required
- **YouTube URL**: The YouTube video URL to analyze (supports both youtu.be and youtube.com formats)
- **Gemini API Key**: Your Google Gemini API key (get it from https://aistudio.google.com/app/apikey)

### Optional
- **YouTube Cookies**: YouTube cookies in Netscape format (required for age-restricted or bot-protected videos)
- **Extract Important Timestamps**: Extract timestamps of important moments, key topics, and significant discussions (enabled by default)

## Output

The Actor outputs a structured dataset with the following fields:

```json
{
  "video_url": "https://youtu.be/VIDEO_ID",
  "comprehensive_summary": "Detailed analysis including participants, topics, recommendations...",
  "key_quotes_insights": "Important quotes, business advice, problems and solutions...",
  "video_structure_analysis": "Video type, length, flow, and distinct sections...",
  "file_id": "files/gemini_file_id",
  "important_timestamps": "[00:45] Introduction: Speaker introduces main topic - Sets context for discussion\n[02:30] Key Insight: Important business advice shared - Critical for understanding strategy..."
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
4. **Analyze**: Runs comprehensive analysis queries:
   - Comprehensive summary analysis
   - Key quotes and insights extraction
   - Video structure analysis
   - Important timestamps extraction (if enabled)
5. **Output**: Saves results to Apify dataset
6. **Cleanup**: Removes temporary video files

## Setup Instructions

### Getting Your Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key and paste it into the "Gemini API Key" field

### YouTube Cookies (Optional but Recommended)
YouTube now often requires authentication to download videos. If you encounter "Sign in to confirm you're not a bot" errors:

1. **Install a browser extension** like "Get cookies.txt LOCALLY" or "cookies.txt"
2. **Visit YouTube** and sign in to your account
3. **Export cookies** using the extension (Netscape format)
4. **Paste the cookies** into the "YouTube Cookies" field

**Alternative methods**:
- Follow the [yt-dlp cookie guide](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp)
- Use browser developer tools to export cookies manually

### Security
- Your API key and cookies are handled securely and marked as secrets in Apify
- Sensitive data is never logged or exposed in the output
- Each user provides their own credentials for maximum security and control

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
  "youtube_url": "https://youtu.be/VIDEO_ID",
  "gemini_api_key": "AIzaSyC...",
  "youtube_cookies": "# Netscape HTTP Cookie File\n# This is a generated file..." 
}
```

## Example Output

```json
{
  "video_url": "https://youtu.be/VIDEO_ID",
  "comprehensive_summary": "Here's a detailed analysis of the video:\n\n**1. Detailed Summary...**",
  "key_quotes_insights": "Here are the key details from the video:\n\n1. Key quotes/insights...",
  "video_structure_analysis": "Okay, here is an analysis of the structure and format...",
  "file_id": "files/GEMINI_FILE_ID"
}
```

## Support

For issues or questions about this Actor, please contact the developer or check the Apify documentation.
