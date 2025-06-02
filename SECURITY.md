# Security Policy

## API Key Management

This Actor follows security best practices for API key management:

### 🔒 No Hardcoded Keys
- **No API keys are hardcoded** in the source code
- All API keys are provided by users through secure input fields
- Each user provides their own API key for maximum security and control

### 🛡️ User-Provided Keys
- Users provide their own Gemini API key through Apify's secure input system
- API keys are marked as secrets and handled securely
- No shared or default API keys - each user has full control

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
- Always provide your own API key
- Use Apify's secret management features
- Regularly update dependencies
- Monitor Actor logs for security issues

## Dependencies Security

This Actor uses the following main dependencies:
- `apify` - Official Apify SDK
- `google-generativeai` - Official Google Gemini SDK
- `yt-dlp` - Popular YouTube downloader

All dependencies are regularly updated to address security vulnerabilities.
