const orb = document.querySelector(".orb");
const thinking = document.querySelector(".thinking");
const responseText = document.querySelector("#response-text");
const responseBox = document.querySelector(".response");


function idle() {
    orb.classList.remove("speaking");
    thinking.style.display = "none";
}


function think() {
    orb.classList.remove("speaking");
    thinking.style.display = "flex";
}


function speak(text) {
    thinking.style.display = "none";
    orb.classList.add("speaking");

    if (text) {
        responseText.textContent = text;
        responseBox.classList.add("visible");
    }
}


function updateState(data) {
    console.log("État reçu :", data);

    if (data.status === "idle") {
        idle();
    }

    if (data.status === "thinking") {
        think();
    }

    if (data.status === "speaking") {
        speak(data.text);
    }
}


async function checkState() {
    try {
        const result = await fetch(
            "http://127.0.0.1:5000/state"
        );

        const data = await result.json();

        updateState(data);

    } catch (error) {
        console.error("Erreur connexion Flask :", error);
    }
}


setInterval(checkState, 100);
checkState();