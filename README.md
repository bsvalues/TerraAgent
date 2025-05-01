# TerraAgent - PACS Training Assistant

An AI-powered platform for PACS training that leverages advanced natural language processing to translate user queries into SQL, with robust document retrieval capabilities and an intuitive, user-friendly chat interface.

## Features

- **Natural Language Processing (NLP)**: Converts user questions into SQL queries
- **Document Retrieval (RAG)**: Provides answers from ingested documents
- **Real-time Chat Interface**: Accessible, responsive web application
- **PostgreSQL Integration**: Efficient database querying and data analysis
- **Property Assessment Tools**: Includes levy calculator and neighborhood trend analysis
- **Monitoring & Analytics**: Comprehensive dashboard with system status and metrics
- **Accessibility Features**: Screen reader support, keyboard navigation, and ARIA attributes

## Quick Deploy

1. Click the "Deploy" button in Replit to deploy the application
2. Set up the required environment variables when prompted
3. Access your application at your-replit-url.replit.app

## Technologies Used

- **Backend**: Python 3.10+, Flask, SQLAlchemy, LangChain
- **Database**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5
- **Accessibility**: ARIA attributes, keyboard navigation, screen reader support
- **Monitoring**: Prometheus, structured logging

## Environment Variables

Set the following environment variables in your deployment:

- `DATABASE_URL`: PostgreSQL connection string (automatically set by Replit)
- `OPENAI_API_KEY`: Your OpenAI API key for AI model access
- `SESSION_SECRET`: Secret key for session management (set to a strong random value)

## Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/your-organization/terraagent.git
   cd terraagent
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up environment variables (create a .env file)

4. Run the application:
   ```bash
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

5. Access the application at http://localhost:5000

## One-Click Deployment

### Using Replit

1. Open your project in Replit
2. Click on the "Deploy" button in the top-right corner
3. Choose your deployment plan
4. Review the configuration settings
5. Click "Deploy" to start the deployment process
6. Once deployed, you'll receive a URL for your application

### Desktop Deployment

For local desktop deployment, we've provided one-click deployment scripts:

#### On Linux/Mac:
```bash
# Make the script executable
chmod +x start_application.sh

# Run the application
./start_application.sh
```

#### On Windows:
```
# Simply double-click on the batch file
start_application.bat
```

The scripts will:
1. Check for Python installation
2. Set up a virtual environment
3. Install required dependencies
4. Create a template .env file if needed
5. Start the application on http://localhost:5000

### Creating Deployment Packages

You can easily create distribution packages for desktop deployment using our build scripts:

#### On Linux/Mac:
```bash
# Make the script executable
chmod +x build_deployment.sh

# Run the build script
./build_deployment.sh
```

#### On Windows:
```
# Simply double-click on
build_deployment.bat
```

These scripts will:
1. Create a deployment directory with all required files
2. Set up template configuration files
3. Include quick start guides
4. Package everything into a ZIP archive ready for distribution
5. The resulting `terraagent_deployment.zip` can be shared with end-users

### Windows Desktop Shortcut

For Windows users, we provide an additional script to create a desktop shortcut for truly one-click access:

1. Extract the deployment package
2. Run `create_desktop_shortcut.bat`
3. A desktop shortcut will be created automatically
4. Double-click the shortcut to launch TerraAgent

This provides the simplest possible experience for end-users who simply want to start the application with a single click.

### Deployment Checklist

- [ ] Database connection is configured
- [ ] OpenAI API key is set in environment variables
- [ ] Session secret is configured
- [ ] Server is configured to listen on the correct port (0.0.0.0:5000)
- [ ] All dependencies are installed (see dependencies.md)

## Accessibility Features

TerraAgent prioritizes accessibility with the following features:

- **Keyboard Navigation**: Full keyboard support with helpful shortcuts
- **Screen Reader Compatibility**: ARIA attributes and semantic HTML
- **Skip to Content**: Keyboard-accessible link to bypass navigation
- **High Contrast**: Visual elements designed for readability
- **Focus Indicators**: Clear visual focus states
- **Responsive Design**: Works on various screen sizes and devices

## Contact

For questions or support, please contact your IT administrator or open an issue in the repository.