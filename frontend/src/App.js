import React from "react";
import './App.css';
import SearchPhotos from "./searchPhotos"

function App() {
  return (
    <div className="App">
      <div className="container">
        <h1 className="title">Gawdi</h1>
        <h2 className="sousTitle">Biometric Search Engine</h2>
        <SearchPhotos />
      </div>
    </div>
  );
}

export default App;
