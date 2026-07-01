import FrontPage from "./FontPage";
import TextAnaliser from "./TextAnaliser";
import Details from "./Details.jsx";
import Home from "./Home.jsx";
import Contact from "./Contact.jsx";
import Socials from "./Socials.jsx";
import EnhancedVoiceComponent from "./EnhancedVoiceComponent.jsx";
import EnhancedFaceComponent from "./EnhancedFaceComponent.jsx";


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

            
            {
                path: "/voice_analiser",
                element: <EnhancedVoiceComponent chatId={1} />
            },

            {
                path: "/face_analiser",
                element: <EnhancedFaceComponent chatId={1} />
            } ,
        ],

    }
]

export default my_routes