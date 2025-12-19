document.addEventListener("DOMContentLoaded", () => {
  const groups = [];
  const container = document.querySelector(".section-importance");

  if (container) {
    const sliders = container.querySelectorAll(".slider");
    const values = container.querySelectorAll(".slider-value");

    sliders.forEach((slider, index) => {
      groups.push({
        slider: slider,
        number: values[index],
        index: index,
      });
    });
  }

  const TOTAL_TARGET = 100;

  function updateSliders(activeIndex, newVal) {
    newVal = Math.max(0, Math.min(TOTAL_TARGET, newVal));

    groups[activeIndex].slider.value = newVal;
    groups[activeIndex].number.value = newVal;

    let currentSum = 0;
    groups.forEach((g) => (currentSum += parseInt(g.slider.value)));

    let difference = currentSum - TOTAL_TARGET;

    while (difference !== 0) {
      if (difference > 0) {
        let candidate = null;
        let maxVal = -1;
        groups.forEach((g, i) => {
          if (i !== activeIndex) {
            let val = parseInt(g.slider.value);
            if (val > 0 && val > maxVal) {
              maxVal = val;
              candidate = g;
            }
          }
        });
        if (candidate) {
          let v = parseInt(candidate.slider.value) - 1;
          candidate.slider.value = v;
          candidate.number.value = v;
          difference--;
        } else {
          newVal--;
          groups[activeIndex].slider.value = newVal;
          groups[activeIndex].number.value = newVal;
          difference--;
        }
      } else if (difference < 0) {
        let candidate = null;
        let minVal = 101;
        groups.forEach((g, i) => {
          if (i !== activeIndex) {
            let val = parseInt(g.slider.value);
            if (val < 100 && val < minVal) {
              minVal = val;
              candidate = g;
            }
          }
        });
        if (candidate) {
          let v = parseInt(candidate.slider.value) + 1;
          candidate.slider.value = v;
          candidate.number.value = v;
          difference++;
        } else {
          difference++;
        }
      }
    }
  }

  groups.forEach((group) => {
    group.slider.addEventListener("input", (e) => {
      updateSliders(group.index, parseInt(e.target.value));
    });
    group.number.addEventListener("input", (e) => {
      let val = parseInt(e.target.value);
      if (isNaN(val)) val = 0;
      updateSliders(group.index, val);
    });
    group.slider.addEventListener("change", (e) => {
      updateSliders(group.index, parseInt(e.target.value));
    });
  });
});
