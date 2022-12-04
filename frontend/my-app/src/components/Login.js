import "./Login.css";
import { useEffect, useState } from "react";

export const Login = () => {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [emailDirty, setemailDirty] = useState(false)
    const [passwordDirty, setpasswordDirty] = useState(false)
    const [emailError, setemailError] = useState('Email не может быть апустым')
    const [passwordError, setpasswordError] = useState('Пароль не может быть пустым')
    const [formValid, setFormValid] = useState(false)

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
    return (
    <h1>
      <form className="loginForm">
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