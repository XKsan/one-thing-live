const orb = document.querySelector(".orb");
const entry = document.querySelector(".entry");
const discovery = document.querySelector(".discovery");

const title = document.getElementById("title");
const reveal = document.getElementById("reveal");
const meaning = document.getElementById("meaning");

const save = document.getElementById("save");
const share = document.getElementById("share");


let data = null;
let opened = false;



const fallback = {

    id: "fallback",

    category: "COSMOS",

    title: {
        en: "THE SUN IS NOT YELLOW",
        zh: "太阳其实不是黄色的"
    },

    reveal: {
        en: "From space, the Sun appears white. Earth's atmosphere changes the color humans experience from the ground.",
        zh: "从太空看，太阳其实呈现白色。地球大气层改变了我们从地面看到的颜色。"
    },

    meaning: {
        en: "Reality is often shaped by the distance between what exists and what we perceive.",
        zh: "我们看到的现实，往往受到观察距离和方式的影响。"
    },

    visual: {

        theme:"cosmos",

        color:"#7B8CFF"

    }

};





async function loadContent(){


    try{


        const response =
        await fetch(
            "./content/today.json",
            {
                cache:"no-store"
            }
        );


        if(!response.ok){

            throw new Error(
                "Content loading failed"
            );

        }


        data =
        await response.json();


    }


    catch(error){


        console.warn(error);


        data =
        fallback;


    }



    renderContent();


    applyVisual();


}







function renderContent(){



    title.innerHTML = `

        <div class="english">

            ${data.title.en}

        </div>


        <div class="chinese">

            ${data.title.zh}

        </div>

    `;



    reveal.innerHTML = `

        <div class="english">

            ${data.reveal.en}

        </div>


        <div class="chinese">

            ${data.reveal.zh}

        </div>

    `;



    meaning.innerHTML = `

        <div class="english">

            ${data.meaning.en}

        </div>


        <div class="chinese">

            ${data.meaning.zh}

        </div>

    `;



}







function applyVisual(){



    const color =
    data.visual?.color
    ||
    "#ffffff";



    document.documentElement.style
    .setProperty(
        "--theme",
        color
    );



    const theme =
    data.visual?.theme
    ||
    "cosmos";



    document.body.dataset.theme =
    theme.toLowerCase();



}







function enterDiscovery(){


    if(opened){

        return;

    }


    opened=true;



    orb.classList.add(
        "portal"
    );


    entry.classList.add(
        "vanish"
    );



    setTimeout(()=>{


        orb.style.display =
        "none";


        entry.style.display =
        "none";



        discovery.classList.remove(
            "hidden"
        );



    },1200);



}







orb.addEventListener(

    "click",

    enterDiscovery

);



entry.addEventListener(

    "click",

    enterDiscovery

);









save.addEventListener(

"click",

()=>{


    localStorage.setItem(

        "ONE_THING_SAVE",

        JSON.stringify(data)

    );


    save.innerText =
    "SAVED";



}

);









share.addEventListener(

"click",

async()=>{


    const text = `

${data.title.en}

${data.title.zh}


${data.reveal.en}

${data.reveal.zh}


— ONE THING

`;



    try{


        if(
            navigator.share
        ){


            await navigator.share({

                title:"ONE THING",

                text:text

            });


        }


        else{


            await navigator.clipboard.writeText(
                text
            );


            share.innerText =
            "COPIED";


        }



    }


    catch(error){


        console.log(
            "Share cancelled"
        );


    }



}

);









// Keyboard support for desktop testing

document.addEventListener(

"keydown",

(event)=>{


    if(
        event.key==="Enter"
    ){

        enterDiscovery();

    }


}

);








// Initialize

loadContent();