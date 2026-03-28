import FrontPage from "./FontPage";
import TextAnaliser from "./TextAnaliser";
import InterfaceBox from "./ChooseInterfaceBox.jsx"

const my_routes = [
    {
        path: "/",
        element: <FrontPage />,

        children: [
            {
                path: "/text_analiser",
                element: <TextAnaliser />,
            } ,

            
            // {
            //     path: "voice_analyzer",
            //     element: <Voice />
            // },

            // {
            //     path: "facial_analyser",
            //     element: <Facial />
            // } ,

            // nav buttons
            // {
            //     path: "/contact",
            //     element: <Contact />,
            // } ,

            // {
            //     path: "/details",
            //     element: <Details />,
            // } ,

            // {
            //     path: "/Socials",
            //     element: <Socials />,
            // } ,

                        // {
            //     path: "/contact",
            //     element: <Contact />,
            // } ,

        ]
    }
]

export default my_routes