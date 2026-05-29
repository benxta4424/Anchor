import FrontPage from "./FontPage";
import TextAnaliser from "./TextAnaliser";
import Details from "./Details.jsx";
import Home from "./Home.jsx";
import Contact from "./Contact.jsx";
import Socials from "./Socials.jsx";


const my_routes = [
    {
        path: "/",
        element: <FrontPage />,

        children: [
            {
                index:true,
                element: <Home />
            },

            {
                path:"/details",
                element: <Details />
            },

            {
                path:"/contact",
                element: <Contact />
            },

            {
                path: "/socials",
                element:<Socials />
            } ,






            {
                path: "/text_analiser",
                element: <TextAnaliser />,
            } ,

            
            // {
            //     path: "voice_analyzer",
            //     element: <Voice />
            // },

            // {
            //     path: "/facial_analyser",
            //     element: <FaceRecognition />
            // } 
        ],

    }
]

export default my_routes