import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './css_files/index.css'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import my_routes from './Components/routes'

// Import illustrations for pre-caching
import textAnalyserIcon from "./img/iconBoxOne.jpg"
import faceAnalyserIcon from "./img/iconBoxTwo.jpg"
import voiceAnalyserIcon from "./img/iconBoxThree.jpg"

// Preload images into browser cache to avoid display flicker
[textAnalyserIcon, faceAnalyserIcon, voiceAnalyserIcon].forEach((src) => {
  const img = new Image();
  img.src = src;
});

// styling files
import "./css_files/frontPage.css"
import "./css_files/choosingBox.css"
import "./css_files/index.css"
import "./css_files/details.css"
import "./css_files/contact.css"
import "./css_files/socials.css"
import "./css_files/textAnaliser.css"
import "./css_files/energencyPopup.css"
import "./css_files/clinicalChart.css"
import "./css_files/dashboard.css"
import "./css_files/voicePatterns.css"
import "./css_files/facePatterns.css"


const routes = createBrowserRouter(my_routes)

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={ routes } />
  </StrictMode>,
)
