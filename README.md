# Chapter X React Example

This is a simple React application created as an example for Chapter X. It demonstrates the basic structure of a React app and how to deploy it on GitHub Pages.

## Getting Started

To get started with this project, follow the instructions below.

### Prerequisites

Make sure you have [Node.js](https://nodejs.org/) installed on your machine. You can check if you have it installed by running:

```
node -v
```

### Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/chapter-x-react-example.git
   ```

2. Navigate to the project directory:

   ```
   cd chapter-x-react-example
   ```

3. Install the dependencies:

   ```
   npm install
   ```

### Running the Application

To run the application in development mode, use the following command:

```
npm start
```

This will start the development server and open the application in your default web browser. You can view it at `http://localhost:3000`.

### Building for Production

To create a production build of the application, run:

```
npm run build
```

This will generate a `build` folder containing the optimized application.

### Manual

Just generate build folder with npm run predeploy

### Deploying to GitHub Pages via library

To deploy the application to GitHub Pages, follow these steps:

1. Install the `gh-pages` package:

   ```
   npm install --save gh-pages
   ```

2. Add the following properties to your `package.json`:

   ```json
   "homepage": "https://yourusername.github.io/chapter-x-react-example",
   "scripts": {
     "predeploy": "npm run build",
     "deploy": "gh-pages -d build"
   }
   ```

3. Deploy the application:

   ```
   npm run deploy
   ```

Your application should now be live on GitHub Pages!

## License

This project is licensed under the MIT License.