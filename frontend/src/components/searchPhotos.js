import React, { useState } from "react";
import axios from "axios";
import Modal from 'react-bootstrap/Modal'
import Filters from "./Filters";
import ReactTooltip from 'react-tooltip';


const data = require("./figure_captions.json")

export default function SearchPhotos() {
  const [query, setQuery] = useState("");
  const [pics, setPics] = useState([]);
  // const [summary, setSummary] = useState({ index: 0, text: '' })
  const [modalShow, setModalShow] = useState(false);
  const [pic, setPic] = useState("");
  const [caption, setCaption] = useState("");
  const [paragraphText, setParagraphText] = useState("");
  const [summaryText, setSummaryText] = useState("");
  //filters states :
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
console.log(summaryText)


  const searchPhotos = async (e) => {
    e.preventDefault();
   
    //axios.post(`http://35.224.166.241:8000/search/`, { keywords: query, option: checks}) 
    axios.post(`http://localhost:8000/search/`, { keywords: query, option: checks}) 
      .then(res => {
        //const figs = res.data.map(f => f.figure.replace('/', '-').replace('_fig', '.pdf_figure_'))
        //const urls = figs.map(f => '/figures/' + f)
        console.log(res.data)
        //setPics(urls.map((f, i) => {         
        //  return { doi: "doi_value_1", score: "score_value", paragraph_text: "text_value_1", figure_ref: "figure_ref_value", caption: "caption_value_1", url: f + '.png',   summary:"summary_text blablabala,lds "  }
        //}
        //))
      })
  };

  console.log(pics)
  
  const handleName = (i, c, p) => {
    setPic(i);
    setCaption(c);
    setParagraphText(p)
    
    setModalShow(true);
  };

  const [isHovering, setIsHovering] = useState(false);

  const handleMouseOver = (s) => {
    setSummaryText(s);
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
          <div class="col-lg-3 col-md-20 mt-4" onClick={() => setModalShow(true)} >

            <img
               onMouseOver={() => handleMouseOver(pic.summary)} 
              data-tip={`${summaryText}`}
              onClick={() => handleName(pic.url, pic.caption, pic.paragraph_text)}
              src={pic.url}
              class="img-thumbnail"
              alt={pic.alt}
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
            <h2>Caption</h2>
            <p className="modalText">{caption}</p>
            <h2>Paragraph</h2>
            <p className="modalText">{paragraphText}</p>
          </Modal.Body>
        </Modal>
      </div>
    </>
  );
}
