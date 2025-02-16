// Global error handler
window.onerror = function (msg, url, lineNo, columnNo, error) {
  console.error(
    "Error: " +
      msg +
      "\nURL: " +
      url +
      "\nLine: " +
      lineNo +
      "\nColumn: " +
      columnNo +
      "\nError object: " +
      JSON.stringify(error)
  );
  return false;
};

function getBHKValue() {
  try {
    const uiBHK = document.getElementsByName("uiBHK");
    for (const radio of uiBHK) {
      if (radio.checked) {
        return parseInt(radio.value);
      }
    }
    throw new Error("No BHK value selected");
  } catch (error) {
    console.error("Error in getBHKValue:", error);
    return -1;
  }
}

function getBathValue() {
  try {
    const uiBathrooms = document.getElementsByName("uiBathrooms");
    for (const radio of uiBathrooms) {
      if (radio.checked) {
        return parseInt(radio.value);
      }
    }
    throw new Error("No bathroom value selected");
  } catch (error) {
    console.error("Error in getBathValue:", error);
    return -1;
  }
}

function onClickedEstimatePrice() {
  try {
    console.log("Estimate price button clicked");

    // Get input values
    const sqft = document.getElementById("uiSqft").value;
    const bhk = getBHKValue();
    const bathrooms = getBathValue();
    const location = document.getElementById("uiLocations").value;
    const estPrice = document.getElementById("uiEstimatedPrice");

    // Validate inputs
    if (!sqft || sqft <= 0) {
      alert("Please enter a valid square footage");
      return;
    }
    if (bhk === -1) {
      alert("Please select number of bedrooms");
      return;
    }
    if (bathrooms === -1) {
      alert("Please select number of bathrooms");
      return;
    }
    if (!location) {
      alert("Please select a location");
      return;
    }

    // Update UI to show loading state
    estPrice.querySelector("h2").textContent = "Estimating Price...";

    const url = "http://127.0.0.1:5000/api/predict_home_price";

    $.ajax({
      url: url,
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        total_sqft: parseFloat(sqft),
        bhk: bhk,
        bath: bathrooms,
        location: location,
      }),
      success: function (data) {
        if (data.error) {
          console.error("Error from server:", data.error);
          estPrice.querySelector("h2").textContent = "Error: " + data.error;
          return;
        }
        console.log("Estimated price:", data.estimated_price);
        estPrice.querySelector("h2").textContent =
          "Estimated Price: " + data.estimated_price.toString() + " Lakh";
      },
      error: function (jqXHR, textStatus, errorThrown) {
        console.error("Error estimating price:", textStatus, errorThrown);
        if (jqXHR.responseJSON && jqXHR.responseJSON.error) {
          estPrice.querySelector("h2").textContent =
            "Error: " + jqXHR.responseJSON.error;
        } else {
          estPrice.querySelector("h2").textContent =
            "Error: Could not estimate price. Please try again.";
        }
      },
      timeout: 10000, // 10 second timeout
    });
  } catch (error) {
    console.error("Error in onClickedEstimatePrice:", error);
    document
      .getElementById("uiEstimatedPrice")
      .querySelector("h2").textContent = "An unexpected error occurred";
  }
}

function onPageLoad() {
  try {
    console.log("document loaded");
    const url = "http://127.0.0.1:5000/api/get_location_names";

    // Show loading state
    const uiLocations = document.getElementById("uiLocations");
    uiLocations.innerHTML = '<option value="">Loading locations...</option>';

    $.ajax({
      url: url,
      method: "GET",
      timeout: 10000, // 10 second timeout
      success: function (data) {
        console.log("got response for get_location_names request");
        if (data.error) {
          console.error("Error loading locations:", data.error);
          uiLocations.innerHTML =
            '<option value="">Error loading locations</option>';
          return;
        }

        if (data && Array.isArray(data.locations)) {
          const locations = data.locations;
          $("#uiLocations").empty();

          // Add default option
          $("#uiLocations").append(
            '<option value="">Select a location</option>'
          );

          // Sort locations alphabetically
          locations.sort().forEach(function (location) {
            const opt = new Option(location);
            $("#uiLocations").append(opt);
          });
        } else {
          console.error("Invalid location data received");
          uiLocations.innerHTML =
            '<option value="">Error: Invalid data</option>';
        }
      },
      error: function (jqXHR, textStatus, errorThrown) {
        console.error("Error fetching locations:", textStatus, errorThrown);
        uiLocations.innerHTML =
          '<option value="">Failed to load locations</option>';
      },
    });
  } catch (error) {
    console.error("Error in onPageLoad:", error);
    document.getElementById("uiLocations").innerHTML =
      '<option value="">Error loading locations</option>';
  }
}

// Remove the updateEstimatedPrice function as it's not needed

// Add event listeners when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  // Initialize the page
  onPageLoad();

  // Add form validation
  const sqftInput = document.getElementById("uiSqft");
  if (sqftInput) {
    sqftInput.addEventListener("input", function () {
      if (this.value < 0) this.value = 0;
    });
  }

  // Add error handling for missing elements
  const requiredElements = ["uiSqft", "uiLocations", "uiEstimatedPrice"];
  requiredElements.forEach((id) => {
    if (!document.getElementById(id)) {
      console.error(`Required element #${id} not found in the document`);
    }
  });
});

// Export functions for testing if needed
if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    getBHKValue,
    getBathValue,
    onClickedEstimatePrice,
    onPageLoad,
  };
}
