import React from 'react'
import LogoCeebios from "../logos/ceebios.png"
import DataForGood from "../logos/DFG.png"

export default function NavBar() {
    return (
     <>
     <nav className='navBar'>
        <img src={LogoCeebios} alt="logo"></img>
        <img src={DataForGood} alt="logo" className='dataLogo'></img>
     </nav>
     </>
    );
  }
  

