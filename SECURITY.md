# Security Policy

## API Key Management

This Actor follows security best practices for API key management:

### 🔒 No Hardcoded Keys
- **No API keys are hardcoded** in the source code
- All sensitive credentials are managed through environment variables
- The default API key (if available) is stored as `GEMINI_API_KEY` environment variable

### 🛡️ Environment Variables
- `GEMINI_API_KEY`: Default Gemini API key (configured by maintainer)
- User-provided keys are handled securely through Apify's input system

### 📋 Security Checklist
- ✅ No exposed API keys in source code
- ✅ Environment variables for sensitive data
- ✅ Secure input handling for user-provided keys
- ✅ Proper error messages without exposing sensitive information
- ✅ Temporary file cleanup after processing

## Reporting Security Issues

If you discover a security vulnerability, please report it by:

1. **Do NOT** open a public GitHub issue
2. Contact the maintainer directly through GitHub
3. Provide detailed information about the vulnerability
4. Allow reasonable time for the issue to be addressed

## Best Practices for Users

### When Using Your Own API Key
- Keep your Gemini API key secure and private
- Don't share your API key in public forums or repositories
- Regularly rotate your API keys
- Monitor your API usage for unexpected activity

### When Self-Hosting
- Set environment variables securely
- Use Apify's secret management features
- Regularly update dependencies
- Monitor Actor logs for security issues

## Dependencies Security

This Actor uses the following main dependencies:
- `apify` - Official Apify SDK
- `google-generativeai` - Official Google Gemini SDK
- `yt-dlp` - Popular YouTube downloader

All dependencies are regularly updated to address security vulnerabilities.
