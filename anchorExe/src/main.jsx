import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './css_files/index.css'
import {createBrowser, RouterProvider} from 'react-router-dom'
import my_routes from './Components/routes'

const routes = createBrowser(my_routes)

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider routes={my_routes} />
  </StrictMode>,
)
