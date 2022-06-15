import React from 'react'
import LogoCeebios from "../logos/ceebios.png"
import DataForGood from "../logos/DFG.png"

export default function Footer() {
    return (
        <>
            {/* Footer */}
            <footer className="text-center text-lg-start bg-light text-muted">
                {/* <!-- Section: Social media --> */}
                <section
                    className="d-flex justify-content-center justify-content-lg-between p-4 border-bottom"
                >
                    {/* <!-- Left --> */}
                    {/* <div className="me-5 d-none d-lg-block">
                        <span>Get connected with us on social networks:</span>
                    </div> */}
                    {/* <!-- Left --> */}

                    {/* <!-- Right --> */}
                    {/* <div>
      <a href="" className="me-4 text-reset">
        <i className="fab fa-facebook-f"></i>
      </a>
      <a href="" className="me-4 text-reset">
        <i className="fab fa-twitter"></i>
      </a>
      <a href="" className="me-4 text-reset">
        <i className="fab fa-google"></i>
      </a>
      <a href="" className="me-4 text-reset">
        <i className="fab fa-instagram"></i>
      </a>
      <a href="" className="me-4 text-reset">
        <i className="fab fa-linkedin"></i>
      </a>
      <a href="" className="me-4 text-reset">
        <i className="fab fa-github"></i>
      </a>
    </div> */}
                    {/* <!-- Right --> */}
                </section>
                {/* <!-- Section: Social media --> */}

                {/* <!-- Section: Links  --> */}
                <section className="">
                    <div className="container h-25 text-center text-md-start mt-5">
                        {/* <!-- Grid row --> */}
                        <div className="row mt-3">
                            {/* <!-- Grid column --> */}
                            <div className="col-md-3 col-lg-4 col-xl-3 mx-auto mb-4">
                                {/* <!-- Content --> */}
                                <h6 className="text-uppercase fw-bold mb-4">
                                    <i className="fa-solid fa-dove me-3"></i>Ceebios
                                </h6>
                                <p>
                                Réseau national d’acteurs industriels, académiques et institutionnels, Ceebios a pour objectif d’accélérer la transition écologique et sociétale par le biomimétisme.
                                
                                </p>
                            </div>
                            {/* <!-- Grid column -->

        <!-- Grid column --> */}
                            <div className="col-md-3 col-lg-4 col-xl-3 mx-auto mb-4">
                                {/* <!-- Links --> */}
                                <h6 className="text-uppercase fw-bold mb-4">
                                    <i className="fa-solid fa-kiwi-bird me-3"></i>
                                    DataForGood
                                </h6>
                                <p>
                                    <a className="text-reset">Association (loi 1901) 100% bénévole créée en 2014 qui rassemble une communauté de 2500+ volontaires tech souhaitant mettre leurs compétences à profit d'associations et d'ONG et de s'engager pour l'intérêt général.</a>
                                </p>
                            </div>
                            {/* <!-- Grid column --> */}

                            {/* <!-- Grid column --> */}
                            <div className="col-md-3 col-lg-2 col-xl-2 mx-auto mb-4">
                                {/* <!-- Links --> */}
                                <h6 className="text-uppercase fw-bold mb-4">
                                    links
                                </h6>
                                <p>
                                    <a href="https://ceebios.com/la-scic-ceebios/" className="text-reset">About Ceebios</a>
                                </p>
                                <p>
                                    <a href="https://ceebios.com/qui-sommes-nous/" className="text-reset">Qui ?</a>
                                </p>
                                <p>
                                    <a href="https://ceebios.com/biomimetisme/" className="text-reset">Biomimétisme</a>
                                </p>
                                <p>
                                    <a href="https://github.com/ceebios/d4g-season-10" className="text-reset">Github</a>
                                </p>
                            </div>
                            {/* <!-- Grid column --> */}

                            {/* <!-- Grid column --> */}
                            <div className="col-md-4 col-lg-3 col-xl-3 mx-auto mb-md-0 mb-4">
                                {/* <!-- Links --> */}
                                <h6 className="text-uppercase fw-bold mb-4">
                                    Contact
                                </h6>
                                <p><i className="fas fa-home me-3"></i> Ceebios SCIC - 62 rue du Faubourg Saint-Martin, 60300 Senlis </p>
                                
                                <p>
                                    <i className="fas fa-envelope me-3"></i>
                                    contact@ceebios.com
                                </p>
                                <div  className="d-flex">
                                <a href="https://twitter.com/ceebios"> <i className="fab fa-twitter me-3"></i></a>
                                <a href="https://www.facebook.com/CEEBIOS/"> <i className="fab fa-facebook"></i></a>
                                </div>
                                
                               
                            </div>
                            {/* <!-- Grid column --> */}
                        </div>
                        {/* <!-- Grid row --> */}
                    </div>
                </section>
                {/* <!-- Section: Links  --> */}

                {/* <!-- Copyright --> */}
                <div className="text-center p-4 "  >
                    © 2022 Copyright:
                    <a className="text-reset fw-bold" href="https://ceebios.com/"> Ceebios</a>
                </div>
                {/* <!-- Copyright --> */}
            </footer>
            {/* <!-- Footer --> */}
        </>
    );
}
