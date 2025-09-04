
# Encryption Management Procedure

# Owner

# Approver

# Last Reviewed

# Scope and applicability

The Encryption management procedure applies to all [Company Name]'s highly confidential and confidential information. Encryption protection must be applied at any storage means (servers, laptops, removable media) and while transmitting through any channels (web, internal network, etc.).

# Encryption standards

# Data Transmission

[Company Name] uses [Cloud Hosting Service] for its production infrastructure. The provider automatically encrypts all VM-to-VM traffic within a VPC network and peered VPC.

The Engineering team configures encryption of data channels of [Company Name]’s applications between end-users and applications backend, following the encryption standards:

<table>
<tbody><tr>
<td>Encryption method</td>
<td>[Company Name]’s standard</td>
</tr>
<tr>
<td>Transport Layer Security</td>
<td>TLS 1.2</td>
</tr>
<tr>
<td>Secure Copy Protocol</td>
<td>At least AES 128</td>
</tr>
<tr>
<td>Digital Signatures</td>
<td>DSA, with key size of at least 1024</td>
</tr>
<tr>
<td></td>
<td>RSA, with key size of at least 1024</td>
</tr>
</tbody></table>

# Data Storage

Encryption Management Procedure

---

[Cloud Hosting Service]

on which [Company Name]'s customers' data resides, encrypts all customer content stored at rest using AES256, except a small number of Persistent Disks created before 2015 that use AES128. Data for storage is split into chunks, and each chunk is encrypted with a unique data encryption key. These data encryption keys are stored with the data, encrypted with ("wrapped" by) key encryption keys exclusively stored and used inside [Cloud Hosting Service]'s central Key Management Service. [Cloud Hosting Service]'s Key Management Service is redundant and globally distributed.

The Engineering team configures additional encryption of data, following the encryption standards:

<table>
<tbody><tr>
<th>Encryption method</th>
<th>[Company Name]ʼs standard</th>
</tr>
<tr>
<td>Advanced Encryption Standard</td>
<td>AES 128 and AES 256</td>
</tr>
<tr>
<td>Secure Hash Algorithm</td>
<td>SHA 2 and SHA 3</td>
</tr>
<tr>
<td>Secure Password Storing</td>
<td>bcrypt hashing function</td>
</tr>
</tbody></table>

# Exceptions

Requests for an exception in the [Company Name]ʼs production environment must be submitted to the VP of Engineering for approval. Requests for an exception in [Company Name]ʼs IT environment must be submitted to the Director of Engineering, Operations. They record information about the approved exception in their teamsʼ working space.

# Key management standards

[Company Name] uses the cryptographic keys in the following cases:

<table>
<tbody><tr>
<th>Case</th>
<th>Responsibility</th>
</tr>
<tr>
<td>Encryption Management Procedure</td>
<td>2</td>
</tr>
</tbody></table>



---

# Encryption Management Procedure

To protect customersʼ data, [Cloud Hosting Service] is responsible for key management in [Cloud Hosting Service].

Web certificate for the Certification authority CA is responsible for key management of [Company Name]ʼs website.

During usage of different vendors, vendors are responsible for key management.

# Further, the procedure defines the requirements for key management for which [Company Name]ʼs internal teams are responsible.

# Keys generation and distribution

Engineers use [Company Name]ʼs internal application to generate SSH keys to access the production environment. Engineers use their own keys to authenticate to specific servers. The engineers do not obtain direct access to the keys.

# Keys revocation/destruction

Once the information has been re-keyed with a new key or keys are compromised, all copies must be destroyed.

# Keys storage

Tunnel SSH keys are stored within the [Company Name]ʼs internal application. Upon expiry, keys are automatically deleted. Application security keys are backed up within key management systems used by [Company Name].

# Violations &#x26; Enforcement

Any known violations of this procedure should be reported to the VP of Engineering. Violations of this policy can result in immediate withdrawal or suspension of system and network privileges and/or disciplinary action according to company procedures, including termination of employment.

---

# Encryption Management Procedure

<table>
<tbody><tr>
<th>Version</th>
<th>Date</th>
<th>Description</th>
<th>Author</th>
<th>Approved by</th>
</tr>
<tr>
<td>4</td>
<td></td>
<td></td>
<td></td>
<td></td>
</tr>
</tbody></table>

