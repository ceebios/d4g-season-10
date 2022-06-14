import React from 'react'



export default function Filters({checks, setChecks}) {

    return (
        <>
            <div className='checkboxGroup'>
                {
                    Object.entries(checks).map(([key,value])=>{
                        return (
                        <div className="checkbox">
                            <input type="checkbox" checked={value} id={key} name={key} onChange={(e)=>setChecks({...checks,[key]:!value})} />
                            <label className='labelCheck' for={key}>{key}</label>
                        </div>)                      
                    })
                }
            </div>
        </>
    );
}


