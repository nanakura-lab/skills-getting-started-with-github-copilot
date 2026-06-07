document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        
        // Create participants list HTML
        let participantsHTML = '<div class="participants-section"><strong>登録者:</strong>';
        if (details.participants.length > 0) {
          participantsHTML += '<ul class="participants-list">';
          details.participants.forEach(participant => {
            participantsHTML += `<li><div class="participant-item"><span>${participant}</span><button class="delete-btn" data-activity="${name}" data-email="${participant}" title="登録解除">✕</button></div></li>`;
          });
          participantsHTML += '</ul>';
        } else {
          participantsHTML += '<p class="no-participants">まだ登録者がいません</p>';
        }
        participantsHTML += '</div>';

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>スケジュール:</strong> ${details.schedule}</p>
          <p><strong>空き枠:</strong> ${spotsLeft}人分</p>
          ${participantsHTML}
        `;

        // Add delete button event listeners
        activityCard.querySelectorAll('.delete-btn').forEach(btn => {
          btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const activityName = btn.getAttribute('data-activity');
            const email = btn.getAttribute('data-email');
            await cancelSignup(activityName, email);
          });
        });

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Function to cancel signup
  async function cancelSignup(activityName, email) {
    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activityName)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        // Refresh activities
        setTimeout(() => {
          fetchActivities();
        }, 500);
      } else {
        messageDiv.textContent = result.detail || "登録解除に失敗しました";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "登録解除に失敗しました。もう一度お試しください。";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error canceling signup:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Refresh activities to show the new participant
        setTimeout(() => {
          fetchActivities();
        }, 1000);
      } else {
        messageDiv.textContent = result.detail || "エラーが発生しました";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "登録に失敗しました。もう一度お試しください。";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
