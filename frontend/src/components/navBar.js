import React from 'react'
import LogoCeebios from "../logos/ceebios.png"
import DataForGood from "../logos/DFG.png"

export default function NavBar() {
    return (
        <>
            <nav className="navbar navbar-custom navbar-light bg-white py-2sm">
                <span className="navbar-brand" >
                   <a href='https://ceebios.com/' target="_blank"><img src={LogoCeebios} alt="logo" className='ceebiosLogo'></img></a>                    
                   <a href='https://dataforgood.fr/' target="_blank"><img src={DataForGood} alt="logo" className='dataLogo'></img></a> 
                </span>
            </nav>
        </>
    );
  }
  

