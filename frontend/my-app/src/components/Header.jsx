import React from "react";
import { UserContext } from "../context/UserContext";
import { useContext } from "react";

const Header = ({title}) => {
    const [token, setToken] = useContext(UserContext)

    const handleLogout = () => {
        
    };

    return(
        <div className="has-text-centered m-6">
            <h1 className="title">{title}</h1>
            {token && (<button className="button">Выйти</button>)}
        </div>
    )
};

export default Header;