import React from "react";
import './App.css';
import SearchPhotos from "./components/searchPhotos"
import NavBar from "./components/navBar";

export default function App() {
  return (
    <div className="App">
      <NavBar/>
      <div className="container">        
        <h1 className="title">Gawdi</h1>
        <h2 className="sousTitle">Biomimetic Image Search Engine</h2>
        <SearchPhotos />
      </div>
    </div>
  );
}

 