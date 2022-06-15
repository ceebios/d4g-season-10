import React, { useState } from "react";
import axios from "axios";
import Modal from 'react-bootstrap/Modal'
import Filters from "./Filters";
import ReactTooltip from 'react-tooltip';

export default function SearchPhotos() {
  const [query, setQuery] = useState("");
  const [pics, setPics] = useState([]);
  const [modalShow, setModalShow] = useState(false);
  const [pic, setPic] = useState("");
  const [paragraphText, setParagraphText] = useState("");
  const [summary, setSummary] = useState("");
  const [checks, setChecks] = useState({
      Map:true,
      Molecules: true,
      PhotoMacro: true,
      PhotoMicro: true,
      Plots: true,
      Table: true,
      DrawingSimu: true
    }
  );


  const searchPhotos = async (e) => {
    e.preventDefault();
   
    axios.post(`http://35.224.166.241:8000/search/`, { keywords: query, option: checks}) 
    //axios.post(`http://localhost:8000/search/`, { keywords: query, option: checks}) 
      .then(res => {
        console.log(res.data)
        setPics(res.data)
      })
  };
 
  const handleName = (i, p) => { 
    setSummary("")
    setPic(i);
    setParagraphText(p)
    setModalShow(true);
    axios.post(`http://35.224.166.241:8000/summarize/`, { text: p}) 
      .then(res => {
        setSummary(res.data)
      })       
  };


  return (
    <>
      <form className="input-group rounded" onSubmit={searchPhotos}>
        <input type="search" className="form-control rounded h-110 " aria-label="Search" aria-describedby="search-addon" rows="4"
          name="query"
          placeholder={`Try "UV protection"`}
          value={query}
          onChange={(e) => setQuery(e.target.value)} />
        <span className="input-group-text border-0" id="search-addon">
          <i className="fas fa-search fa-2x " onClick={searchPhotos}></i>
        </span>
      </form>

      <Filters checks={checks} setChecks={setChecks}/>

      <div className="row mt-4" >
        {pics.map((pic, i) =>
          <div className="col-lg-3 col-md-20 mt-4" onClick={() => setModalShow(true)} >

            <img
              data-tip={`${pic.caption}`}
              onClick={() => handleName("./images/images/"+pic.url.replace('/','-')+'.jpg', pic.paragraph_text)}
              src={"./images/images/"+pic.url.replace('/','-')+'.jpg'}
              className="img-thumbnail"
              alt={pic.url}
            />
            {/* {i === summary.index ? <p className="figcaption">{pic.summary}</p> : <></>} */}
            {/* <p > Summary </p> */}

        <ReactTooltip className="tooltip" effect="solid" />

          </div>
        
          )
        }
       
        <Modal       
          data={setPic}
          show={modalShow}
          onHide={() => setModalShow(false)} >
          <Modal.Body><img className="modalImage" src={pic}></img>
            <h2>Summary</h2>
            <p className="modalText">{summary}</p>
            <h2>Paragraph</h2>
            <p className="modalText">{paragraphText}</p>
          </Modal.Body>
        </Modal>
      </div>
    </>
  );
}
