import React, { useState } from "react";
import Unsplash, { toJson } from "unsplash-js";
import axios from "axios";

export default function SearchPhotos() {

 //states to save information    
    const [query, setQuery] = useState(""); 
    const [pics, setPics] = useState([]);
    const [summary, setSummary] = useState({index:0,text:''})

    const searchPhotos = async (e) => {
      e.preventDefault();
    
     axios.get(`http://127.0.0.1:8000/search/`+encodeURIComponent(query)) //34.135.15.52
      .then(res => {
        const figs = res.data.map(f=>f.figure.replace('/','-').replace('_fig','.pdf_figure_'))
        const urls = figs.map(f=>'/figures/'+f)
        setPics(urls.map((f,i)=>{
          return {url:f+'.png', alt:res.data[i].caption, id:f+i,paragraph:res.data[i].paragraph}
        }
        ))
      })  
    };
    
    const getSummary = async(e,i)=>{
      e.preventDefault();
      console.log(pics[i].paragraph)
      axios.post("http://127.0.0.1:8000/summarize",{text:pics[i].paragraph}).then(res=>setSummary({index:i,text:res.data[0]}))
    }

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
        {pics.map((pic,i) => 
        <div className="card" key={pic.id}>
          <figure className="figure" onClick={(e)=>getSummary(e,i)} >
            <img
                className="card-image"
                alt={pic.alt}
                src={pic.url}
                width="70%"
                height="70%"
                onError={(event) => event.target.style.display = 'none'}
            ></img>
            <p className="figcaption">{pic.alt}</p>
          </figure>
          {i===summary.index?<p className="figcaption">{summary.text}</p>:<></>}
        </div>)
        }  
        
      </div>
    </>
  );
}
