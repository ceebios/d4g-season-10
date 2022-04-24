import React, { useState } from "react";
import Unsplash, { toJson } from "unsplash-js";
import axios from "axios";


const unsplash = new Unsplash({
  accessKey: "6Whjn95ROo8cNvevQvtv8-Tx3fgtda_g82EidsfJdz4",
});


export default function SearchPhotos() {

 //states to save information    
    const [query, setQuery] = useState(""); 
    const [pics, setPics] = useState([]);

    


   const searchPhotos = async (e) => {
      e.preventDefault();
    
     /* axios.get(`http://34.135.15.52:8000/search/keywords/`+encodeURIComponent(query))
      .then(res => {

        const urls = res.urls;
        setPics(res.urls);
        console.log(res);
      })*/  
      unsplash.search
        .photos(query)
        .then(3)
        .then(toJson)
        .then((json) => {
          setPics(json.results);
        });
      console.log("Submitting the Form");
    };
    

  return (
    <>
      <form className="form" onSubmit={searchPhotos}>
        <label className="label" htmlFor="query">
        </label>
        <input
          type="text"
          name="query"
          className="input"
          placeholder={`Try "dog" or "apple"`}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" className="button">
          Search
        </button>
      </form>
      <div className="card-list">
      
         {pics.map((pic) => <div className="card" key={pic.id}>
        <figure>
         <img
                className="card--image"
                alt={pic.alt_description}
                src={pic.urls.full}
                width="50%"
                height="50%"
              ></img>
             <figcaption>{pic.alt_description}</figcaption>
              </figure>
         </div>)}  
        
      </div>
    </>
  );
}