import { useNavigate, Link } from "react-router-dom";

export const Navbar = () => {
    const navigate = useNavigate()
    return(
        <div className="App">
        <header class="d-flex flex-wrap align-items-center justify-content-center justify-content-md-between py-3 mb-4 border-bottom">
        <a href="/" class="d-flex align-items-center col-md-3 mb-2 mb-md-0 text-dark text-decoration-none">
          <svg class="bi me-2" width="40" height="32" role="img" aria-label="Bootstrap"></svg>
        </a>
  
        <ul class="nav col-12 col-md-auto mb-2 justify-content-center mb-md-0">
          <li><Link to='/' class="nav-link px-2 link-secondary">Home</Link></li>
          <li><a href="#" class="nav-link px-2 link-dark">Features</a></li>
          <li><a href="#" class="nav-link px-2 link-dark">Pricing</a></li>
          <li><a href="#" class="nav-link px-2 link-dark">FAQs</a></li>
          <li><a href="#" class="nav-link px-2 link-dark">About</a></li>
        </ul>
  
        <div class="px-2 col-md-3 text-end">
          <button href="/login" type="button" class="px-2 btn btn-primary" onClick={() => navigate('/login')}>Login</button>
          <button href="/sighup" type="button" class="px-2 btn btn-primary" onClick={() => navigate('/registration')}>Sign-up</button>
        </div>
      </header>
      </div>
    );
}
