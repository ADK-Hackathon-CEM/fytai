# Fitness Assistant App

A Flutter application that provides a fitness assistant with chat capabilities, calendar integration, and user management.

## Features

- 🤖 **AI Chat Assistant** - Get fitness advice and workout recommendations
- 📅 **Calendar Integration** - Schedule and manage your workouts
- 🔐 **User Authentication** - Secure login with Google Sign-In
- 📱 **Cross-Platform** - Works on Android, iOS, Web, and Desktop
- 🔥 **Firebase Integration** - Real-time data synchronization
- 🎯 **Personalized Experience** - User profiles and preferences

## Prerequisites

- Flutter SDK (3.8.1 or higher)
- Dart SDK
- Android Studio / VS Code
- Firebase project
- Python backend server (for AI chat functionality)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd adk-hackathon-bof/frontend
```

### 2. Install Dependencies
```bash
flutter pub get
```

### 3. Firebase Setup

#### Configure Firebase
1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Authentication (Google Sign-In)
3. Enable Firestore Database
4. Add your app to Firebase (Android, iOS, Web)

#### Generate Firebase Configuration
```bash
# Install FlutterFire CLI
dart pub global activate flutterfire_cli

# Configure Firebase for your project
flutterfire configure
```

### 4. Environment Configuration

#### Create Environment File
```bash
# Copy the example environment file
cp env.example .env
```

#### Edit Environment Variables
Open `.env` and configure your backend server URL:
```bash
# Backend Server Configuration
BACKEND_URL=http://your-backend-ip:5000
```

**Note**: Replace `your-backend-ip` with your actual backend server IP address.

### 5. Backend Server Setup

Make sure your Python backend server is running and accessible at the URL specified in your `.env` file.

## Running the App

### Development Mode
```bash
flutter run
```

### Build for Production

#### Android
```bash
flutter build apk --release
```

#### iOS
```bash
flutter build ios --release
```

#### Web
```bash
flutter build web --release
```

## Project Structure

```
lib/
├── data/
│   └── notifiers.dart          # State management
├── services/
│   ├── auth_service.dart       # Authentication logic
│   ├── database_service.dart   # Firestore operations
│   └── env_service.dart        # Environment variables
├── views/
│   ├── pages/                  # Main app screens
│   │   ├── chat_page.dart      # AI chat interface
│   │   ├── home_page.dart      # Dashboard
│   │   ├── calendar_page.dart  # Calendar view
│   │   ├── profile_page.dart   # User profile
│   │   ├── login_page.dart     # Authentication
│   │   └── register_page.dart  # User registration
│   ├── widgets/                # Reusable components
│   └── widget_tree.dart        # App navigation
└── main.dart                   # App entry point
```

## Configuration

### Environment Variables

The app uses the following environment variables:

- `BACKEND_URL`: URL of the Python backend server

### Firebase Configuration

The app requires Firebase configuration for:
- User authentication
- Real-time database
- Cloud Firestore

## Troubleshooting

### Common Issues

1. **Firebase Configuration Error**
   - Ensure `flutterfire configure` was run successfully
   - Check that `firebase_options.dart` exists

2. **Backend Connection Error**
   - Verify the backend server is running
   - Check the `BACKEND_URL` in your `.env` file
   - Ensure the IP address is accessible from your device

3. **Build Errors**
   - Run `flutter clean` and `flutter pub get`
   - Check Flutter and Dart SDK versions

### Getting Help

If you encounter issues:
1. Check the Flutter documentation
2. Review Firebase setup guides
3. Check the backend server logs