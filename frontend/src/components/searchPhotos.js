import React, { useState } from "react";
import axios from "axios";
import Modal from 'react-bootstrap/Modal'


const data = require("./figure_captions.json")

export default function SearchPhotos() {
  const [query, setQuery] = useState("");
  const [pics, setPics] = useState([]);
  const [summary, setSummary] = useState({ index: 0, text: '' })
  const [modalShow, setModalShow] = useState(false);
  const [pic, setPic] = useState("");
  const [text, setText] = useState("");


  const searchPhotos = async (e) => {
    e.preventDefault();
    console.log(data)
    axios.get(`http://35.197.87.106:8000/search/` + encodeURIComponent(query)) //34.135.15.52
      .then(res => {
        const figs = res.data.map(f => f.figure.replace('/', '-').replace('_fig', '.pdf_figure_'))
        const urls = figs.map(f => '/figures/' + f)
        setPics(urls.map((f, i) => {
          console.log(f + '.png')
          return { url: f + '.png', alt: data[figs[i] + '.png'], id: f + i, paragraph: res.data[i].paragraph }
        }
        ))
      })
  };

  const getSummary = async (e, i) => {
    e.preventDefault();
    console.log(pics[i].paragraph)
    axios.post("http://34.105.13.154:8000/summarize", { text: pics[i].paragraph }).then(res => setSummary({ index: i, text: res.data[0] }))
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
