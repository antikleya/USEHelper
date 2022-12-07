import { useParams } from "react-router-dom";
import React, { useContext, useEffect, useState } from "react";

import {UserContext} from "../context/UserContext";

export const Themes = () => {
    const params = useParams()
    const subjectId = params.subjectId

    const [token] = useContext(UserContext);
    const [subject, setSubject] = useState(null);
    const [loaded, setLoaded] = useState(false);
    const [activeModal, setActiveModal] = useState(false);
    const [id, setId] = useState(null);

    const getSubject = async () => {
        const requestOptions = {
            method: "GET",
            headers: {"Content-Type" : "application/json"},
        };
        const response = await fetch("/api/subjects/"+subjectId, requestOptions);
        if (!response.ok) {
            alert('Что-то пошло не так')
        } else {
        const data = await response.json();
        setSubject(data);
        setLoaded(true);
        }
    };

    useEffect(() => {
        getSubject();
    }, []);

    return(
    <>
        {loaded && subject ? (
            <div id="table">
            <h5>{subject.name}</h5>
            {subject.themes.map(({name, description}) => (
                <div class="card">
                <div class="card-body">
                    <h5 class="card-title">{name}</h5>
                    <p class="card-text">{description}</p>
                </div>
                </div>
            ))}
        </div>
        ) : (<p>Загрузка</p>)}
    </>
    );
}