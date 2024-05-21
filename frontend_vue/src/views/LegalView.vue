<template>
  <AppLayoutOneColumn>
    <ol>
      <li>
        <h4>1. Introduction</h4>
        <p>
          1.1. We provide the Canarytokens service free of charge. We do so as a
          public service because we believe that everyone should be able to
          detect attackers and compromises.
        </p>
        <p>1.2. We will work hard to keep the service up and running.</p>
        <p>
          1.3. We love technical creativity, so you can use the service for any
          lawful purpose, but there are some ways you can never use
          Canarytokens.
        </p>
        <p>
          1.4. If you use the service for a purpose that we don’t allow
          <a href="#cant-do">(covered below)</a> or help others (people or
          algorithms) do so, you breach the policy, and we may suspend or
          terminate your use of the service. (There is a good chance you are
          also a jerk).
        </p>
      </li>
      <li>
        <h4>2. What we do with your information</h4>
        <p>
          2.1. We don't sell the information you provide to us when you use this
          service.
        </p>
        <p>
          2.2. We sometimes make use of third parties when providing the service
          (like mail delivery via Mailgun or use of AWS for hosting). We keep
          them to a minimum, we vet them carefully, and we never give away more
          information than is needed to make the service work.
        </p>
      </li>
      <li>
        <h4>3. Your actions have consequences</h4>
        <p>
          3.1. You understand that your actions could have legal consequences
          and may result in criminal or civil liability. We do not endorse, take
          responsibility, or accept liability for your actions.
        </p>
      </li>
      <li id="cant-do">
        <h4>4. What you can’t do</h4>
        <p>
          4.1. You may not use, or help others to use, Canarytokens for any
          illegal or harmful purposes.
        </p>
        <p>
          4.2. You may not use, or help others to use, Canarytokens to interfere
          unlawfully with the connections or security of networks, systems, or
          other users.
        </p>
        <p>
          4.3 You may not use (or abuse) the system to cause a disruption to
          other users.
        </p>
      </li>
      <li>
        <h4>5. Investigation and enforcement</h4>
        <p>
          5.1. We will investigate any potential breaches of this policy. During
          and after an investigation, we can alter or remove any content that
          breaches this policy and (while we are aware that snitches get
          stitches) may share this content or related information with any
          relevant third party, including law enforcement agencies.
        </p>
      </li>
      <li>
        <h4>6. Changes</h4>
        <p>
          6.1. We may change the terms of this policy at any time. We will
          notify you of any changes by placing a notice on the legal page of
          this website. If you disagree with the change, you must stop using the
          services. If you continue to use the services following notification
          of a change to the terms, the changed terms will apply to you, and you
          will be deemed to have accepted such terms.
        </p>
      </li>
    </ol>
  </AppLayoutOneColumn>
</template>

<script setup lang="ts">
import AppLayoutOneColumn from '@/layout/AppLayoutOneColumn.vue';
</script>

<style scoped>
h4 {
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
  font-size: 1.3rem;
}

li > p {
  margin-left: 1rem;
  margin-bottom: 1rem;
}
</style>
