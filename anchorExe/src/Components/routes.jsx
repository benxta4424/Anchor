import FrontPage from "./FontPage";
import TextAnaliser from "./TextAnaliser";


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
            //     path: "/contact",
            //     element: <Contact />,
            // } ,
        ]
    }
]

export default my_routes