import React from 'react'
import LogoCeebios from "../logos/ceebios.png"
import DataForGood from "../logos/DFG.png"

export default function Footer() {
    return (
        <>
            {/* Footer */}
            <footer class="text-center text-lg-start bg-light text-muted">
                {/* <!-- Section: Social media --> */}
                <section
                    class="d-flex justify-content-center justify-content-lg-between p-4 border-bottom"
                >
                    {/* <!-- Left --> */}
                    {/* <div class="me-5 d-none d-lg-block">
                        <span>Get connected with us on social networks:</span>
                    </div> */}
                    {/* <!-- Left --> */}

                    {/* <!-- Right --> */}
                    {/* <div>
      <a href="" class="me-4 text-reset">
        <i class="fab fa-facebook-f"></i>
      </a>
      <a href="" class="me-4 text-reset">
        <i class="fab fa-twitter"></i>
      </a>
      <a href="" class="me-4 text-reset">
        <i class="fab fa-google"></i>
      </a>
      <a href="" class="me-4 text-reset">
        <i class="fab fa-instagram"></i>
      </a>
      <a href="" class="me-4 text-reset">
        <i class="fab fa-linkedin"></i>
      </a>
      <a href="" class="me-4 text-reset">
        <i class="fab fa-github"></i>
      </a>
    </div> */}
                    {/* <!-- Right --> */}
                </section>
                {/* <!-- Section: Social media --> */}

                {/* <!-- Section: Links  --> */}
                <section class="">
                    <div class="container h-25 text-center text-md-start mt-4">
                        {/* <!-- Grid row --> */}
                        <div class="row ">
                            {/* <!-- Grid column --> */}
                            <div class="col-md-3 col-lg-4 col-xl-3 mx-auto mb-4">
                                {/* <!-- Content --> */}
                                <h6 class="text-uppercase fw-bold mb-4">
                                    <i class="fa-solid fa-dove me-3"></i>Ceebios
                                </h6>
                                <p>
                                Réseau national d’acteurs industriels, académiques et institutionnels, Ceebios a pour objectif d’accélérer la transition écologique et sociétale par le biomimétisme.
                                
                                </p>
                            </div>
                            {/* <!-- Grid column -->

        <!-- Grid column --> */}
                            <div class="col-md-3 col-lg-4 col-xl-3 mx-auto mb-2">
                                {/* <!-- Links --> */}
                                <h6 class="text-uppercase fw-bold mb-4">
                                    <i class="fa-solid fa-kiwi-bird me-3"></i>
                                    DataForGood
                                </h6>
                                <p>
                                    <a class="text-reset">Association (loi 1901) 100% bénévole créée en 2014 qui rassemble une communauté de 2500+ volontaires tech souhaitant mettre leurs compétences à profit d'associations et d'ONG et de s'engager pour l'intérêt général.</a>
                                </p>
                            </div>
                            {/* <!-- Grid column --> */}

                            {/* <!-- Grid column --> */}
                            <div class="col-md-3 col-lg-2 col-xl-2 mx-auto mb-4">
                                {/* <!-- Links --> */}
                                <h6 class="text-uppercase fw-bold mb-4">
                                    links
                                </h6>
                                <p>
                                    <a href="https://ceebios.com/la-scic-ceebios/" class="text-reset">About Ceebios</a>
                                </p>
                                <p>
                                    <a href="https://ceebios.com/qui-sommes-nous/" class="text-reset">Qui ?</a>
                                </p>
                                <p>
                                    <a href="https://ceebios.com/biomimetisme/" class="text-reset">Biomimétisme</a>
                                </p>
                                <p>
                                    <a href="https://github.com/ceebios/d4g-season-10" class="text-reset">Github</a>
                                </p>
                            </div>
                            {/* <!-- Grid column --> */}

                            {/* <!-- Grid column --> */}
                            <div class="col-md-4 col-lg-3 col-xl-3 mx-auto mb-md-0 mb-4">
                                {/* <!-- Links --> */}
                                <h6 class="text-uppercase fw-bold mb-4">
                                    Contact
                                </h6>
                                <p><i class="fas fa-home me-3"></i> Ceebios SCIC - 62 rue du Faubourg Saint-Martin, 60300 Senlis </p>
                                
                                <p>
                                    <i class="fas fa-envelope me-3"></i>
                                    contact@ceebios.com
                                </p>
                                <div  class="d-flex">
                                <a href="https://twitter.com/ceebios"> <i class="fab fa-twitter me-3"></i></a>
                                <a href="https://www.facebook.com/CEEBIOS/"> <i class="fab fa-facebook"></i></a>
                                </div>
                                
                               
                            </div>
                            {/* <!-- Grid column --> */}
                        </div>
                        {/* <!-- Grid row --> */}
                    </div>
                </section>
                {/* <!-- Section: Links  --> */}

                {/* <!-- Copyright --> */}
                <div class="text-center p-4 "  >
                    © 2022 Copyright:
                    <a class="text-reset fw-bold" href="https://ceebios.com/"> Ceebios</a>
                </div>
                {/* <!-- Copyright --> */}
            </footer>
            {/* <!-- Footer --> */}
        </>
    );
}
