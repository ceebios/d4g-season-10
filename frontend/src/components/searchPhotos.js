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
    
     axios.get(`http://127.0.0.1:8000/search/keywords/`+encodeURIComponent(query)) //34.135.15.52
      .then(res => {
        console.log(res.data)
        const figs = res.data.map(f=>f.figure.replace('/','-').replace('_fig','.pdf_figure_'))
        const urls = figs.map(f=>'/figures/'+f)
        setPics(urls.map((f,i)=>{
          return {url:f+'.png', alt:res.data[i].caption, id:f+i,paragraph:res.data[i].paragraph}
        }
        ))
      })  
      /*
      unsplash.search
        .photos(query)
        .then(3)
        .then(toJson)
        .then((json) => {
          setPics(json.results);
        });
      console.log("Submitting the Form");
      */
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
          placeholder={`Try "UV protection"`}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" className="button">
          Search
        </button>
      </form>
      <div className="card-list">
      
         {pics.map((pic) => <div className="card" key={pic.id}>
        <figure className="figure">
         <img
                className="card-image"
                alt={pic.alt}
                src={pic.url}
                width="70%"
                height="70%"
                onerror="this.onerror=null; this.remove();"
              ></img>
             <p className="figcaption">{pic.alt}</p>
              </figure>
         </div>)}  
        
      </div>
    </>
  );
}