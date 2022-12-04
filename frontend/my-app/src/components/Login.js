import "./Login.css";
import { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { UserContext } from "../context/UserContext";


export const Login = () => {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [emailDirty, setemailDirty] = useState(false)
    const [passwordDirty, setpasswordDirty] = useState(false)
    const [emailError, setemailError] = useState('Email не может быть апустым')
    const [passwordError, setpasswordError] = useState('Пароль не может быть пустым')
    const [formValid, setFormValid] = useState(false)
    const navigate = useNavigate()
    const [,setToken] = useContext(UserContext)

    const handleSubmit = (e) => {
        e.preventDefault();
        submitLogin();
    }

    useEffect(() => {
        if (emailError || passwordError) {
            setFormValid(false)
        } else {
            setFormValid(true)
        }
    }, [emailError, passwordError])

    const blurHandler = (e) => {
        switch (e.target.name) {
            case 'email':
                setemailDirty(true)
                break
            case 'password':
                setpasswordDirty(true) 
                break   
        }
    }

    const emailHandler = (e) => {
        setEmail(e.target.value)
        const re = /^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/i;
        if (!re.test(String(e.target.value).toLowerCase())) {
            setemailError('Некорректный email')
        } else {
            setemailError("")
        }
    }

    const passwordHandler = (e) => {
        setPassword(e.target.value)
        if(e.target.value.length < 3) {
            setpasswordError('Пароль должен быть длиннее 3 символов')
            if (!e.target.value) {
               setpasswordError('Пароль не может быть пустым') 
            }
        }
        else {
            setpasswordError('')
        }
    }

    const submitLogin = async () => {
        const requestOptions = {
            method: "POST",
            headers: {"Content-Type" : "application/x-www-form-urlencoded"},
            body: JSON.stringify(`grant_type=&username=${email}&password=${password}&scope=&client_id=&client_secret=`) ,
        };
        const response = await fetch("/api/token", requestOptions);
        const data = await response.json()

        if (response.ok) {
            setToken(data.access_token);
            navigate("/subjects");
        } else{
            alert("Проверьте правильность данных")
        }
    };

    return (
    <h1>
      <form className="loginForm" onSubmit={handleSubmit}>
        <h2>Авторизация</h2>
        <div>
        {(emailDirty && emailError) && <div style={{color: 'red'}}>{emailError}</div>}
        <input
            onChange={e => emailHandler(e)}
            value={email}
            onBlur={e => blurHandler(e)}
            name="email"
            className="loginFormInput"
            type="text"
            placeholder="Логин"
            required
        />
        </div>
        <div>
        {(passwordDirty && passwordError) && <div style={{color: 'red'}}>{passwordError}</div>}
          <input
            onChange={e => passwordHandler(e)}
            value={password}
            onBlur={e => blurHandler(e)}
            name="password"
            className="loginFormInput"
            type="password"
            placeholder="Пароль"
            required
          />
        </div>
        <div>
          <button disabled={!formValid} className="blackBtn" type="submit">
            Войти
          </button>
        </div>
      </form>
    </h1>
  );
};

export default Login;