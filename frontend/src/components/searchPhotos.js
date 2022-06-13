import React, { useState } from "react";
import axios from "axios";
import Modal from 'react-bootstrap/Modal'
import Filters from "./Filters";


const data = require("./figure_captions.json")

export default function SearchPhotos() {
  const [query, setQuery] = useState("");
  const [pics, setPics] = useState([]);
  const [summary, setSummary] = useState({ index: 0, text: '' })
  const [modalShow, setModalShow] = useState(false);
  const [pic, setPic] = useState("");
  const [text, setText] = useState("");
  const [checks, setChecks] = useState({
    DrawingSimu:true,
    Map:true,
    Molecules: true,
    PhotoMacro: true,
    PhotoMicro: true,
    Plots: true,
    Table: true 
  }
);
console.log(checks)
  const searchPhotos = async (e) => {
    e.preventDefault();
   
    axios.get(`http://35.197.87.106:8000/search/` + encodeURIComponent(query)) //34.135.15.52
    // axios.post(`http://35.197.87.106:8000/search/`, { keywords: query, options: checks}) 
      .then(res => {
        const figs = res.data.map(f => f.figure.replace('/', '-').replace('_fig', '.pdf_figure_'))
        const urls = figs.map(f => '/figures/' + f)
        setPics(urls.map((f, i) => {
         
          return { url: f + '.png', alt: data[figs[i] + '.png'], id: f + i, paragraph: res.data[i].paragraph, summary:"blahodfhvzjfhvkjzdhfvkjhzdfvjk"  }
        }
        ))
      })
  };

  console.log(pics)

  const getSummary = async (e, i) => {
    e.preventDefault();
   
    axios.post("http://35.197.87.106:8000/summarize", { text: pics[i].paragraph }).then(res => setSummary({ index: i, text: res.data[0] }))
  }

  const handleName = (i, t) => {
    setPic(i);
    setText(t)
    setModalShow(true);

  };

  return (
    <>
      <form class="input-group rounded" onSubmit={searchPhotos}>
        <input type="search" className="form-control rounded h-110 " aria-label="Search" aria-describedby="search-addon" rows="4"
          name="query"
          placeholder={`Try "UV protection"`}
          value={query}
          onChange={(e) => setQuery(e.target.value)} />
        <span class="input-group-text border-0" id="search-addon">
          <i class="fas fa-search fa-2x " onClick={searchPhotos}></i>
        </span>
      </form>

      <Filters checks={checks} setChecks={setChecks}/>

      <div class="row mt-4" >
        {pics.map((pic, i) =>
          <div class="col-lg-3 col-md-20 mt-4" onClick={() => setModalShow(true)}>

            <img
              onClick={() => handleName(pic.url, pic.alt)}
              src={pic.url}
              class="img-thumbnail"
              alt={pic.alt}
            />
            {i === summary.index ? <p className="figcaption">{summary.text}</p> : <></>}

          </div>)
        }
        <Modal
          data={setPic}
          show={modalShow}
          onHide={() => setModalShow(false)} >
          <Modal.Body><img className="modalImage" src={pic}></img>
            <p className="modalText">{text}</p>
          </Modal.Body>
        </Modal>
      </div>
    </>
  );
}
