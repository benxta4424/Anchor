import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './css_files/index.css'
import {createBrowser, createBrowserRouter, RouterProvider} from 'react-router-dom'
import my_routes from './Components/routes'

// styling files
import "./css_files/frontPage.css"
import "./css_files/choosingBox.css"
import "./css_files/index.css"

const routes = createBrowserRouter(my_routes)

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider routes={ routes } />
  </StrictMode>,
)
