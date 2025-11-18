# 📱 Social Media Caption Generator

A beautiful, modern web application for automating social media captions for grocery stores. Powered by Google's Gemini AI, this tool analyzes sale ads and generates engaging, platform-ready captions.

## ✨ Features

### 🎨 Modern UI Design
- **Beautiful gradient backgrounds** with deep purple and blue tones
- **Smooth animations** on hover and interactions
- **Glass-morphism effects** with backdrop blur
- **Professional typography** using Inter font
- **Responsive card layouts** with elegant shadows

### 🤖 AI-Powered Analysis
- **Image & Video Analysis**: Upload grocery sale ads in various formats (PNG, JPG, JPEG, WEBP, MP4, MOV, AVI)
- **Automatic Product Detection**: Extracts product names, prices, sale dates, and store information
- **Smart Caption Generation**: Creates engaging captions in multiple languages (English/Spanish)
- **Engagement Questions**: Generates questions to boost viewer interaction

### 📱 Social Media Integration
- **Instagram Mockup Preview**: See how your posts will look before publishing
- **Multiple Caption Tones**: Choose from 11 different tones (Simple, Fun, Excited, Professional, etc.)
- **Hashtag Optimization**: Automatically includes relevant hashtags

### 🏪 Multi-Store Support
- Pre-configured stores: Ted's Fresh Market, La Hacienda Market, La Princesa Market, Mi Tiendita, Viva Supermarket, International Fresh Market, Sam's Foods, RRanch Market
- **Custom Store Definitions**: Add your own stores with custom branding and formatting

### 🎯 Batch Processing
- Analyze and generate captions for multiple items at once
- Select/deselect items for batch processing
- Maintains style consistency across captions

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Google Gemini API key

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd grocerycaption
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API key:
   - Create a `.env` file in the project root
   - Add your Gemini API key: `GEMINI_API_KEY='your_key_here'`

4. Run the application:
```bash
streamlit run app.py
```

## 🎨 UI Highlights

### Color Scheme
- **Primary Gradient**: Deep purple to violet (#667eea → #764ba2)
- **Background**: Dark blue gradients (#0f0c29 → #1a1a2e → #16213e)
- **Accents**: Glowing purple highlights with smooth transitions

### Design Elements
- **3D Card Effects**: Elevated cards with hover animations
- **Smooth Transitions**: All interactions have fluid 0.3s transitions
- **Focus States**: Beautiful glow effects on form inputs
- **Modern Icons**: Emoji-based visual language throughout

## 📊 Usage

1. **Upload Content**: Drag and drop images or videos of sale ads
2. **Analyze**: Click "Analyze" to extract product information
3. **Review & Edit**: Verify detected information and make corrections
4. **Generate**: Create captions with your preferred tone
5. **Preview**: View mockups of how posts will appear on Instagram
6. **Copy & Share**: Copy the generated caption and use it on social media

## 🛠️ Technical Stack

- **Framework**: Streamlit
- **AI/ML**: Google Gemini 2.5 Flash
- **Image Processing**: OpenCV, Pillow
- **Language**: Python 3.12+
- **Styling**: Custom CSS with modern design patterns

## 📝 Version History

### v5.0 (Current) - Major UI Overhaul
- Complete visual redesign with modern gradient backgrounds
- Enhanced card designs with glass-morphism effects
- Smooth animations and transitions throughout
- Improved typography and spacing
- Better color scheme with purple/blue gradients
- Enhanced button designs with hover effects
- Modernized form inputs with focus states
- Instagram-style mockup viewer

### v4.3 (Previous)
- Basic caption generation and store management
- Image/video analysis capabilities
- Multi-language support

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is for educational and commercial use.

## 🙏 Acknowledgments

- Powered by Google Gemini AI
- Built with Streamlit
- Designed for grocery store social media managers
