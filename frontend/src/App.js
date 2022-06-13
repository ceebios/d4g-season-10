import React from "react";
import './App.css';
import SearchPhotos from "./components/searchPhotos"
import NavBar from "./components/navBar";
import GawdiLogo from "./logos/gawdi.png"
import Footer from "./components/Footer";

export default function App() {
  return (
    <>
    <div className="App">
      <NavBar/>
      <div className="container">        
        {/* <h1 className="title">Gawdi</h1> */}
        <div className="LogoAndTitle">
        <img className="gawdiLogo" src={GawdiLogo} alt="logo"></img>
        <h2 className="sousTitle">Biomimetic Image Search Engine</h2>
        </div>
        <SearchPhotos />
      </div>
    </div>
    <Footer/>
    </>
    
  );
}

 