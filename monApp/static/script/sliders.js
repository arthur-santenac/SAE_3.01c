document.addEventListener("DOMContentLoaded", () => {
    const groups = [];
    const container = document.querySelector(".section-importance");
    
    if(container) {
        const sliders = container.querySelectorAll(".slider");
        const values = container.querySelectorAll(".slider-value");
        
        sliders.forEach((slider, index) => {
            groups.push({
                slider: slider,
                number: values[index],
                index: index
            });
        });
    }

    const TOTAL_TARGET = 100;

    let globalTurnIndex = 0;
    
    function updateSliders(activeIndex, newVal) {
        newVal = Math.max(0, Math.min(TOTAL_TARGET, newVal));
        groups[activeIndex].slider.value = newVal;
        groups[activeIndex].number.value = newVal;
        let currentSum = 0;
        groups.forEach(g => currentSum += parseInt(g.slider.value));
        let difference = currentSum - TOTAL_TARGET;
        const otherGroups = groups.filter(g => g.index !== activeIndex);
        let safetyCounter = 500; 
        while (difference !== 0 && safetyCounter > 0) {
            safetyCounter--;
            let currentIndex = globalTurnIndex % otherGroups.length;
            let candidate = otherGroups[currentIndex];
            let val = parseInt(candidate.slider.value);

            let changeMade = false;

            if (difference > 0) {
                if (val > 0) {
                    val--;
                    candidate.slider.value = val;
                    candidate.number.value = val;
                    difference--;
                    changeMade = true;
                }
            } else {
                if (val < TOTAL_TARGET) {
                    val++;
                    candidate.slider.value = val;
                    candidate.number.value = val;
                    difference++;
                    changeMade = true;
                }
            }
            globalTurnIndex++;
        }
    }

    groups.forEach((group) => {
        group.slider.addEventListener('input', (e) => {
            updateSliders(group.index, parseInt(e.target.value));
        });
        group.number.addEventListener('input', (e) => {
            let val = parseInt(e.target.value);
            if (isNaN(val)) val = 0;
            updateSliders(group.index, val);
        });
        group.slider.addEventListener('change', (e) => {
            updateSliders(group.index, parseInt(e.target.value));
        });
    });
});