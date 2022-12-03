//import './App.css';
import {Login} from './components/Login';
import {Navbar} from './components/Navbar';
import { Registration } from './components/Registration';
import {Route, Routes} from 'react-router-dom';
import { Homepage } from './components/Homepage';

export function App() {
  return (
    <>
    <Navbar />
    <Routes>
      <Route path='/login' element={<Login />} />
      <Route path='/registration' element={<Registration />} />
      <Route path='/' element={<Homepage />} />
    </Routes>
    </>
  );

}

export default App;