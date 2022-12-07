import React, { useContext, useEffect, useState } from "react";

import {UserContext} from "../context/UserContext";

const Subjects = () => {
    const [token] = useContext(UserContext);
    const [subjects, setSubjects] = useState(null);
    const [loaded, setLoaded] = useState(false);
    const [activeModal, setActiveModal] = useState(false);
    const [id, setId] = useState(null);

    const getSubjects = async () => {
        const requestOptions = {
            method: "GET",
            headers: {"Content-Type" : "application/json"},
        };
        const response = await fetch("/api/subjects", requestOptions);
        if (!response.ok) {
            alert('Что-то пошло не так')
        } else {
        const data = await response.json();
        setSubjects(data);
        setLoaded(true);
        }
    };

    useEffect(() => {
        getSubjects();
    }, []);

    return(
    <>
        {loaded && subjects ? (
            <div id="table">
            {subjects.map(({name, id}) => (
                <div class="card col-2">
                <img src="" class="card-img-top" />
                <div class="card-body">
                    <h5 class="card-title">{name}</h5>
                    <a href={"/subjects/" + id} class="btn btn-primary">Подробнее</a>
                </div>
                </div>
            ))}
        </div>
        ) : (<p>Загрузка</p>)}
    </>
    );
};

export default Subjects;