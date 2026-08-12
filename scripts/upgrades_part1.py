UPGRADES = {
    1: {
        "visual_rules": [
            ("Route before reachability", "Trace the subnet route table first: an internet gateway serves public IPv4 paths, while a NAT gateway gives private subnets outbound-only internet access."),
            ("State lives in security groups", "Security groups are stateful and attach to ENIs; network ACLs are stateless subnet boundaries, so return traffic must be allowed explicitly."),
            ("Private service paths", "Gateway endpoints keep S3 and DynamoDB traffic off NAT, while interface endpoints use PrivateLink ENIs and security groups for supported services."),
            ("Availability by AZ", "A NAT gateway is zonal. Place one per active Availability Zone and route each private subnet locally to avoid cross-AZ dependency and charges."),
        ],
        "scenarios": [
            {
                "tab": "Private S3",
                "title": "Reach S3 without NAT",
                "body": "Private EC2 instances need S3 access but must not traverse the internet or pay NAT processing charges. Add an S3 gateway endpoint and restrict its endpoint policy and bucket policy. An internet gateway does not make private instances reachable, and an interface endpoint adds unnecessary hourly cost here.",
                "reason": ["No public path", "No NAT charge", "Policy controlled"],
            },
            {
                "tab": "Outbound HA",
                "title": "Resilient private-subnet egress",
                "body": "A two-AZ workload needs outbound patch access and must survive one AZ failure. Deploy a NAT gateway in each AZ and point each private subnet at its local NAT. One shared NAT creates an AZ dependency, while an internet gateway cannot provide outbound access to instances without public addresses.",
                "reason": ["AZ independent", "Outbound only", "Local routing"],
            },
            {
                "tab": "Filter Layers",
                "title": "Block a hostile CIDR",
                "body": "Administrators must deny a known CIDR across every instance in a subnet while retaining application security groups. Add an explicit deny in the subnet network ACL and allow required return ports. Security groups have no deny rules, and route tables are not packet-filtering policy.",
                "reason": ["Explicit deny", "Subnet scope", "Stateless returns"],
            },
        ],
        "quiz": [
            {
                "q": "Private EC2 instances must download objects from S3 without internet routes and with the lowest recurring network cost. Which design meets the requirement?",
                "options": ["A. Add an S3 gateway endpoint", "B. Add a NAT gateway in every AZ", "C. Assign public IPv4 addresses", "D. Add an internet gateway route"],
                "correct": 0,
                "explain": "The deciding constraints are private routing and low recurring cost; an S3 gateway endpoint has no hourly endpoint or NAT processing charge.",
            },
            {
                "q": "A subnet must reject one malicious source CIDR even when an attached application security group allows its port. Which control should be changed?",
                "options": ["A. Security group outbound rule", "B. Network ACL inbound deny rule", "C. Internet gateway route", "D. VPC DHCP option set"],
                "correct": 1,
                "explain": "The deciding constraint is an explicit subnet-level deny. Network ACLs support ordered allow and deny rules, whereas security groups allow only.",
            },
            {
                "q": "Instances in two private subnets across two AZs require highly available IPv4 internet egress. Which architecture removes a single-AZ dependency?",
                "options": ["A. One NAT instance in one AZ", "B. One egress-only internet gateway", "C. A NAT gateway per AZ with local routes", "D. One internet gateway per private subnet"],
                "correct": 2,
                "explain": "The deciding constraint is AZ-resilient IPv4 egress. NAT gateways are zonal, so each subnet should use a NAT in its own AZ.",
            },
            {
                "q": "A security group allows TCP 443 inbound from a client. No outbound rule explicitly allows the response ephemeral port. Why can the response still return?",
                "options": ["A. Route tables open response ports", "B. The internet gateway tracks sessions", "C. Network ACLs are stateful", "D. Security groups are stateful"],
                "correct": 3,
                "explain": "The deciding behavior is connection tracking: security groups automatically permit response traffic for an allowed flow.",
            },
            {
                "q": "An IPv6-only private workload needs outbound internet access but must reject unsolicited inbound internet connections. Which VPC component is appropriate?",
                "options": ["A. Egress-only internet gateway", "B. NAT gateway", "C. Gateway Load Balancer", "D. VPC peering connection"],
                "correct": 0,
                "explain": "The deciding constraints are IPv6 and outbound-only internet access. An egress-only internet gateway provides that behavior without IPv4 NAT.",
            },
        ],
    },
    2: {
        "visual_rules": [
            ("Match topology to scale", "Use peering for a few direct relationships and Transit Gateway for transitive hub-and-spoke routing across many VPCs and attachments."),
            ("Separate path from encryption", "Direct Connect supplies a private physical path but does not encrypt traffic by default; add VPN over DX when encryption is required."),
            ("Publish one service", "PrivateLink exposes a service through interface endpoints without sharing routes or requiring non-overlapping consumer CIDRs."),
            ("Resolve across boundaries", "Route 53 Resolver inbound and outbound endpoints bridge hybrid DNS; private hosted zones alone do not answer on-premises resolvers automatically."),
        ],
        "scenarios": [
            {
                "tab": "Many VPCs",
                "title": "Build a transitive network hub",
                "body": "Dozens of VPCs and two offices need centralized, transitive routing with segmented route domains. Attach them to a Transit Gateway and use separate TGW route tables. A peering mesh grows quadratically and peering cannot route transitively through another VPC.",
                "reason": ["Transitive hub", "Route domains", "Fewer links"],
            },
            {
                "tab": "Stable Hybrid",
                "title": "Private predictable hybrid path",
                "body": "A data center transfers steady large volumes to AWS and requires consistent network performance, with encrypted failover. Use Direct Connect as the primary path and a site-to-site VPN as backup, adding VPN over DX if primary-path encryption is mandatory. VPN alone depends on internet conditions, while Direct Connect alone lacks native encryption.",
                "reason": ["Predictable path", "Encrypted option", "Backup route"],
            },
            {
                "tab": "SaaS Access",
                "title": "Expose only an internal service",
                "body": "A provider must serve hundreds of customer VPCs, including overlapping CIDRs, without granting broad network access. Put the service behind an NLB and publish it through PrivateLink endpoint services. Peering requires non-overlapping CIDRs and exposes routed network reachability beyond the single service.",
                "reason": ["Overlap safe", "Service scoped", "No route sharing"],
            },
        ],
        "quiz": [
            {
                "q": "Fifty VPCs need transitive connectivity to each other and to on-premises networks with centralized route segmentation. Which service best fits?",
                "options": ["A. VPC peering mesh", "B. AWS Transit Gateway", "C. AWS PrivateLink", "D. Route 53 private hosted zone"],
                "correct": 1,
                "explain": "The deciding constraints are transitive routing and scale. Transit Gateway provides a managed hub with multiple route tables.",
            },
            {
                "q": "A partner must consume one TCP service privately from a VPC whose CIDR overlaps the provider VPC. The provider must not share network routes. What should be used?",
                "options": ["A. VPC peering", "B. Transit Gateway peering", "C. PrivateLink endpoint service", "D. Site-to-site VPN"],
                "correct": 2,
                "explain": "The deciding constraints are overlapping CIDRs and service-only exposure. PrivateLink maps endpoint ENIs to a published service without routed connectivity.",
            },
            {
                "q": "A company needs a dedicated, predictable path from its data center to AWS, but all application traffic must also be encrypted in transit. Which design works?",
                "options": ["A. Direct Connect only", "B. Internet gateway with TLS termination disabled", "C. VPC peering over Direct Connect", "D. VPN over Direct Connect"],
                "correct": 3,
                "explain": "The deciding constraints are dedicated performance and encryption. Direct Connect supplies the path, while the VPN supplies IPsec encryption.",
            },
            {
                "q": "On-premises DNS servers must resolve records in Route 53 private hosted zones. Which component accepts those DNS queries inside the VPC?",
                "options": ["A. Route 53 Resolver inbound endpoint", "B. Route 53 Resolver outbound endpoint", "C. Public hosted zone alias", "D. Transit Gateway Connect"],
                "correct": 0,
                "explain": "The deciding direction is on premises to AWS. A Resolver inbound endpoint receives forwarded queries for private AWS namespaces.",
            },
            {
                "q": "Two VPCs have a peering connection, and one is connected to a third VPC. The first VPC cannot reach the third through the second. What explains this?",
                "options": ["A. Peering supports only IPv6 transit", "B. VPC peering is non-transitive", "C. Route 53 blocks peered routes", "D. Security groups cannot reference peers"],
                "correct": 1,
                "explain": "The deciding topology rule is that VPC peering is non-transitive; each required VPC pair needs a direct connection or a routing hub.",
            },
        ],
    },
    3: {
        "visual_rules": [
            ("Choose the load-balancer layer", "ALB makes Layer 7 host and path decisions for HTTP; NLB preserves Layer 4 performance, static IP needs, and TCP or UDP handling."),
            ("Scale replaceable capacity", "Keep instances stateless behind a load balancer and let an Auto Scaling group replace unhealthy capacity across multiple AZs."),
            ("Separate launch from scaling", "A launch template defines instance configuration; target tracking, step, scheduled, or predictive policies decide desired capacity."),
            ("Align every health signal", "Use load balancer health checks with Auto Scaling so instances that boot but cannot serve the application are replaced."),
        ],
        "scenarios": [
            {
                "tab": "HTTP Routes",
                "title": "Route by hostname and path",
                "body": "One HTTPS entry point must route api.example.com and /images to different target groups. Use an ALB with host- and path-based listener rules and ACM certificates. An NLB does not inspect HTTP paths, and DNS routing cannot split requests by URL path.",
                "reason": ["Layer 7 rules", "TLS support", "Target groups"],
            },
            {
                "tab": "Static IP",
                "title": "Serve allowlisted TCP traffic",
                "body": "Partners require fixed IP addresses for a latency-sensitive TCP service deployed across AZs. Use an internet-facing NLB with Elastic IP addresses per enabled AZ. ALB addresses can change and ALB is intended for HTTP-family protocols, while Global Accelerator is unnecessary if regional entry points suffice.",
                "reason": ["Static addresses", "Layer 4", "Cross-AZ service"],
            },
            {
                "tab": "Flash Sale",
                "title": "Scale ahead of a known event",
                "body": "A sale starts at a fixed time and instance initialization takes several minutes. Configure scheduled scaling to raise ASG capacity before the event, then use target tracking for live demand. Reactive scaling alone starts too late, and larger fixed instances waste capacity after the sale.",
                "reason": ["Known schedule", "Warm capacity", "Elastic follow-up"],
            },
        ],
        "quiz": [
            {
                "q": "A web platform must route requests to different target groups based on hostname and URL path while terminating HTTPS. Which load balancer should it use?",
                "options": ["A. Gateway Load Balancer", "B. Network Load Balancer", "C. Application Load Balancer", "D. Classic Load Balancer"],
                "correct": 2,
                "explain": "The deciding constraints are Layer 7 host and path inspection. ALB listener rules provide both and can terminate HTTPS.",
            },
            {
                "q": "External clients allowlist fixed IPv4 addresses for a high-throughput TCP application. Which regional load-balancing design satisfies this?",
                "options": ["A. ALB with sticky sessions", "B. CloudFront with an ALB origin", "C. ASG without a load balancer", "D. NLB with Elastic IPs per AZ"],
                "correct": 3,
                "explain": "The deciding constraints are static IP addresses and TCP performance. NLB supports Layer 4 traffic and per-AZ Elastic IPs.",
            },
            {
                "q": "An ASG instance passes EC2 status checks but its web process is dead. The company wants automatic replacement. What should be configured?",
                "options": ["A. ELB health checks for the ASG", "B. Scheduled scaling every minute", "C. A larger root EBS volume", "D. NACL health probes"],
                "correct": 0,
                "explain": "The deciding constraint is application-level failure. Enabling ELB health checks lets the ASG replace targets that fail the load balancer check.",
            },
            {
                "q": "Traffic tracks CPU utilization unpredictably throughout the day. The ASG should maintain CPU near 50 percent with minimal policy management. Which policy fits?",
                "options": ["A. Scheduled scaling", "B. Target tracking scaling", "C. Manual desired capacity", "D. Instance refresh"],
                "correct": 1,
                "explain": "The deciding constraint is maintaining a metric target under variable load. Target tracking adjusts capacity around the selected CPU value.",
            },
            {
                "q": "A batch fleet can tolerate interruption and needs the lowest EC2 compute cost, but it must replace reclaimed capacity automatically. Which design is best?",
                "options": ["A. Dedicated Hosts in one AZ", "B. On-Demand instances without an ASG", "C. EC2 Auto Scaling with diversified Spot capacity", "D. Reserved Instances with fixed capacity"],
                "correct": 2,
                "explain": "The deciding constraints are interruption tolerance and minimum cost. Diversified Spot in an ASG reduces concentration risk and replaces lost instances.",
            },
        ],
    },
    4: {
        "visual_rules": [
            ("Start with access semantics", "Choose S3 for object APIs, EBS for block storage attached within one AZ, and EFS for shared regional NFS across Linux clients."),
            ("Match FSx to the protocol", "Use FSx for Windows File Server for SMB and Windows integration, and FSx for Lustre for high-performance parallel file workloads."),
            ("Design S3 lifecycle by retrieval need", "Move objects among S3 classes according to access predictability, retrieval latency, retention period, and minimum-duration charges."),
            ("Protect data independently", "Multi-AZ placement is not backup: use EBS snapshots, S3 Versioning and replication, EFS backup, or AWS Backup to meet recovery requirements."),
        ],
        "scenarios": [
            {
                "tab": "Shared Linux",
                "title": "Share files across AZs",
                "body": "A Linux web fleet in three AZs needs concurrent POSIX file access and automatic capacity growth. Mount regional EFS through mount targets in each AZ. EBS volumes are zonal and generally not a shared multi-AZ filesystem, while S3 does not provide native POSIX semantics.",
                "reason": ["Regional NFS", "Concurrent access", "Elastic capacity"],
            },
            {
                "tab": "Archive",
                "title": "Retain rarely retrieved records",
                "body": "Compliance records must remain for seven years, are almost never read, and can tolerate hours before retrieval. Use S3 Glacier Deep Archive with lifecycle transitions and retention controls as required. S3 Standard pays for immediate access that is not needed, while EBS requires provisioned block capacity.",
                "reason": ["Lowest archive cost", "Long retention", "Hours acceptable"],
            },
            {
                "tab": "Windows Share",
                "title": "Migrate an SMB namespace",
                "body": "Windows applications require managed SMB shares, Active Directory integration, and native Windows file features. Use Amazon FSx for Windows File Server joined to the directory. EFS exposes NFS rather than SMB, and S3 object storage cannot preserve normal SMB filesystem behavior.",
                "reason": ["Native SMB", "AD integrated", "Windows features"],
            },
        ],
        "quiz": [
            {
                "q": "Linux instances in three AZs need simultaneous access to a shared POSIX filesystem that grows automatically. Which storage service is appropriate?",
                "options": ["A. A single gp3 EBS volume", "B. Amazon EFS", "C. S3 Glacier Flexible Retrieval", "D. Instance store"],
                "correct": 1,
                "explain": "The deciding constraints are concurrent multi-AZ NFS access and elastic capacity. EFS is a regional managed filesystem built for this pattern.",
            },
            {
                "q": "A high-performance computing workload needs a parallel filesystem integrated with S3 and optimized for very high throughput. Which service should be selected?",
                "options": ["A. FSx for Windows File Server", "B. EFS One Zone", "C. FSx for Lustre", "D. EBS sc1"],
                "correct": 2,
                "explain": "The deciding constraints are parallel HPC I/O and S3 integration. FSx for Lustre is optimized for this workload.",
            },
            {
                "q": "An EC2 database needs durable low-latency block storage, and the instance and volume will remain in one Availability Zone. Which choice fits?",
                "options": ["A. Amazon S3", "B. Amazon EFS", "C. FSx for OpenZFS", "D. Provisioned IOPS EBS"],
                "correct": 3,
                "explain": "The deciding constraints are attached block semantics and predictable low-latency IOPS. Provisioned IOPS EBS is designed for such databases.",
            },
            {
                "q": "Objects are accessed with unpredictable frequency, must remain immediately available, and should automatically move to the cheapest suitable access tier. What fits?",
                "options": ["A. S3 Intelligent-Tiering", "B. S3 One Zone-IA", "C. S3 Glacier Deep Archive", "D. EBS Cold HDD"],
                "correct": 0,
                "explain": "The deciding constraints are unknown access patterns and immediate availability. Intelligent-Tiering monitors access and moves objects among eligible tiers.",
            },
            {
                "q": "A Windows application requires managed SMB shares, Active Directory authentication, and Windows ACL support. Which service meets all requirements?",
                "options": ["A. Amazon EFS", "B. FSx for Windows File Server", "C. S3 File Gateway only", "D. EBS Multi-Attach"],
                "correct": 1,
                "explain": "The deciding constraints are SMB, AD, and Windows ACL semantics. FSx for Windows File Server natively provides them.",
            },
        ],
    },
    5: {
        "visual_rules": [
            ("Choose the data model first", "Use RDS or Aurora for relational joins and transactions; use DynamoDB when known key-based access patterns need massive managed scale."),
            ("Separate HA from read scale", "RDS Multi-AZ provides synchronous standby failover, while read replicas serve reads and can support regional read scaling or DR."),
            ("Cache the right layer", "ElastiCache removes repeated low-latency reads or stores ephemeral state; it does not replace the durable system of record."),
            ("Design DynamoDB keys for traffic", "Partition-key cardinality and even traffic distribution prevent hot partitions; GSIs add alternate query patterns at extra cost."),
        ],
        "scenarios": [
            {
                "tab": "Relational HA",
                "title": "Fail over a transactional database",
                "body": "An order system needs SQL transactions and automatic in-Region failover without application-managed replication. Use RDS Multi-AZ or an Aurora cluster across AZs. A read replica is primarily asynchronous read scaling and may lose recent changes, while DynamoDB requires a data-model rewrite.",
                "reason": ["SQL transactions", "Synchronous HA", "Managed failover"],
            },
            {
                "tab": "Global Keys",
                "title": "Serve active-active user state",
                "body": "Users in multiple Regions need local, low-latency key-value writes with managed multi-Region replication. Use DynamoDB global tables and design conflict-tolerant access patterns. Cross-Region RDS replicas are not active-active writers, and ElastiCache is not the durable source of truth.",
                "reason": ["Local writes", "Multi-Region", "Managed replication"],
            },
            {
                "tab": "Read Cache",
                "title": "Absorb repeated hot queries",
                "body": "A read-heavy application repeatedly requests the same database records and can tolerate brief cache staleness. Add ElastiCache using cache-aside with expiration and invalidation. More Multi-AZ standbys do not serve application reads, while scaling the writer alone wastes database resources.",
                "reason": ["Sub-ms reads", "Offload database", "Staleness allowed"],
            },
        ],
        "quiz": [
            {
                "q": "A relational production database needs automatic failover within one Region and no read-scaling requirement. Which RDS configuration addresses this?",
                "options": ["A. RDS Multi-AZ deployment", "B. One cross-Region read replica", "C. ElastiCache cluster", "D. DynamoDB global table"],
                "correct": 0,
                "explain": "The deciding constraint is in-Region relational high availability. Multi-AZ synchronously maintains a standby and manages failover.",
            },
            {
                "q": "A read-heavy RDS workload needs additional read capacity, and the application can tolerate replica lag. Which change is most direct?",
                "options": ["A. Enable Multi-AZ only", "B. Add RDS read replicas", "C. Increase backup retention", "D. Add a NAT gateway"],
                "correct": 1,
                "explain": "The deciding constraint is read scaling with tolerated lag. Read replicas asynchronously copy data and serve read-only traffic.",
            },
            {
                "q": "A key-value application needs single-digit millisecond performance at very large scale with no server management. Access is by known partition keys. What fits?",
                "options": ["A. Amazon Redshift", "B. RDS for SQL Server", "C. Amazon DynamoDB", "D. Amazon Neptune"],
                "correct": 2,
                "explain": "The deciding constraints are key-based access, massive scale, and serverless operations. DynamoDB directly matches them.",
            },
            {
                "q": "A globally distributed application requires active-active key-value writes in two AWS Regions with managed conflict resolution. Which feature should be used?",
                "options": ["A. Aurora Replica Auto Scaling", "B. RDS Multi-AZ DB cluster", "C. DAX in one Region", "D. DynamoDB global tables"],
                "correct": 3,
                "explain": "The deciding constraint is managed multi-Region active-active writing. DynamoDB global tables replicate writes among participating Regions.",
            },
            {
                "q": "An application repeatedly reads the same catalog entries and can tolerate seconds of staleness. The database is CPU-bound. What is the best optimization?",
                "options": ["A. Add ElastiCache with cache-aside", "B. Convert Multi-AZ to Single-AZ", "C. Disable database indexes", "D. Increase automated backup frequency"],
                "correct": 0,
                "explain": "The deciding constraints are repeated reads and tolerated staleness. Cache-aside offloads hot reads while preserving the database as record.",
            },
        ],
    },
    6: {
        "visual_rules": [
            ("Grant roles, not copied keys", "Use IAM roles and STS temporary credentials for workloads and federation; avoid distributing long-lived IAM user access keys."),
            ("Separate permission layers", "Identity and resource policies grant permissions, permissions boundaries cap identities, and SCPs cap member-account permissions without granting any."),
            ("Control the organization centrally", "Use Organizations OUs and SCPs for guardrails, while delegated administrators and service integrations centralize operations."),
            ("Evaluate the full request", "An effective allow must survive explicit denies, SCPs, boundaries, session policies, identity policies, and applicable resource policies."),
        ],
        "scenarios": [
            {
                "tab": "Cross Account",
                "title": "Read data with a role",
                "body": "An application in Account A needs limited access to a bucket in Account B without shared credentials. Create a role in B with bucket permissions and trust A to assume it through STS, adding external ID conditions for a third party. Copying access keys creates long-lived secret risk, while an SCP cannot grant bucket access.",
                "reason": ["Temporary credentials", "Scoped trust", "No key sharing"],
            },
            {
                "tab": "Region Guard",
                "title": "Restrict member-account Regions",
                "body": "Security must prevent member accounts from creating most resources outside approved Regions, even for account administrators. Attach an SCP with the required deny conditions to the relevant OU, exempting global services carefully. IAM policies in each account are easier to alter, and an SCP alone does not grant permitted actions.",
                "reason": ["OU-wide guardrail", "Admin constrained", "Explicit deny"],
            },
            {
                "tab": "Developer Cap",
                "title": "Delegate role creation safely",
                "body": "Developers may create roles but must never grant permissions beyond a security-approved ceiling. Require a permissions boundary on created roles and restrict iam:PassRole to approved roles. A normal allow policy can be changed into broader access, while an SCP is too coarse for per-role delegated limits.",
                "reason": ["Maximum ceiling", "Delegated creation", "PassRole scoped"],
            },
        ],
        "quiz": [
            {
                "q": "An EC2 application needs access to DynamoDB without storing long-lived credentials on the instance. Which identity mechanism is best?",
                "options": ["A. IAM role attached through an instance profile", "B. Root user access keys", "C. IAM user keys in user data", "D. Shared credentials in an AMI"],
                "correct": 0,
                "explain": "The deciding constraint is avoiding long-lived secrets. An instance role supplies automatically rotated STS credentials.",
            },
            {
                "q": "An SCP attached to an OU allows s3:GetObject, but a user in a member account has no IAM policy granting it. Can the user read objects?",
                "options": ["A. Yes, because SCPs grant permissions", "B. No, because SCPs only set permission guardrails", "C. Yes, if the OU is nested", "D. No, because S3 is excluded from SCPs"],
                "correct": 1,
                "explain": "The deciding fact is that SCPs do not grant permissions. An identity or resource policy must still provide an applicable allow.",
            },
            {
                "q": "Developers can create IAM roles, but every created role must remain below a centrally approved maximum permission set. Which feature enforces that ceiling?",
                "options": ["A. Access Analyzer archive rule", "B. STS external ID", "C. IAM permissions boundary", "D. IAM credential report"],
                "correct": 2,
                "explain": "The deciding constraint is a maximum permission ceiling for delegated identities. A permissions boundary limits what identity policies can make effective.",
            },
            {
                "q": "A vendor assumes a role in a customer account, and the customer wants protection against the confused deputy problem. What condition should be required?",
                "options": ["A. aws:RequestedRegion", "B. aws:MultiFactorAuthAge only", "C. s3:prefix", "D. sts:ExternalId"],
                "correct": 3,
                "explain": "The deciding constraint is identifying the vendor's specific customer context. Requiring a unique external ID mitigates confused deputy role assumption.",
            },
            {
                "q": "An organization must prevent even member-account administrators from disabling a required security service. Which centralized control is appropriate?",
                "options": ["A. An SCP with an explicit deny", "B. A role trust policy", "C. An IAM group in each account", "D. An STS session tag"],
                "correct": 0,
                "explain": "The deciding constraint is organization-level enforcement against member administrators. An applicable SCP explicit deny limits their effective permissions.",
            },
        ],
    },
    7: {
        "visual_rules": [
            ("Place each security control", "KMS protects cryptographic keys, Secrets Manager rotates credentials, WAF filters web requests, and Shield mitigates DDoS attacks."),
            ("Treat key policy as foundational", "KMS authorization depends on the key policy, with IAM grants effective only when the policy enables the relevant account or principal."),
            ("Rotate without exposing secrets", "Store database credentials in Secrets Manager, grant workloads retrieval permission, and use supported or custom rotation workflows."),
            ("Detect before responding", "GuardDuty analyzes signals for threats; Security Hub aggregates posture and findings, while EventBridge and automation perform response actions."),
        ],
        "scenarios": [
            {
                "tab": "Web Abuse",
                "title": "Stop injection and bot requests",
                "body": "A public ALB receives SQL injection attempts and excessive requests from individual clients. Associate an AWS WAF web ACL with managed SQLi rules and a rate-based rule. Security groups cannot inspect HTTP payloads, and Shield focuses on DDoS rather than application query syntax.",
                "reason": ["Layer 7 filter", "Managed rules", "Rate limiting"],
            },
            {
                "tab": "DB Secret",
                "title": "Rotate credentials automatically",
                "body": "A Lambda function needs database credentials that must rotate regularly without redeployment. Store them in Secrets Manager, enable rotation, and grant the function only secret retrieval and required KMS permissions. Environment variables alone retain static values, while Parameter Store standard parameters do not provide native managed rotation.",
                "reason": ["Managed rotation", "Runtime retrieval", "Least privilege"],
            },
            {
                "tab": "Threat Signal",
                "title": "Detect compromised credentials",
                "body": "Security needs managed detection of unusual API calls and known malicious network activity without deploying agents. Enable GuardDuty across accounts and Regions, then route findings through EventBridge for response. WAF sees only supported web traffic, and CloudTrail records API activity but does not itself perform threat analysis.",
                "reason": ["Threat analytics", "No agents", "Automated findings"],
            },
        ],
        "quiz": [
            {
                "q": "A public ALB must block SQL injection patterns and throttle clients that exceed a request threshold. Which service directly supplies both controls?",
                "options": ["A. AWS WAF", "B. AWS Shield Standard", "C. Amazon GuardDuty", "D. AWS KMS"],
                "correct": 0,
                "explain": "The deciding constraints are HTTP payload inspection and rate-based blocking. AWS WAF web ACL rules provide both.",
            },
            {
                "q": "An application needs database passwords stored securely and rotated on a schedule without embedding them in deployment artifacts. Which service is designed for this?",
                "options": ["A. AWS Artifact", "B. AWS Secrets Manager", "C. AWS Shield Advanced", "D. Amazon Inspector"],
                "correct": 1,
                "explain": "The deciding constraint is managed secret rotation. Secrets Manager stores, retrieves, and rotates supported credentials.",
            },
            {
                "q": "Security teams want managed detection of anomalous API behavior and communication with known malicious IP addresses. Which service should they enable?",
                "options": ["A. AWS WAF", "B. AWS Certificate Manager", "C. Amazon GuardDuty", "D. AWS Firewall Manager only"],
                "correct": 2,
                "explain": "The deciding constraint is threat detection from behavioral and network signals. GuardDuty analyzes AWS data sources and emits findings.",
            },
            {
                "q": "A team encrypts data with a customer managed KMS key, but an IAM allow still fails. Which policy is foundational to permitting use of that key?",
                "options": ["A. NACL policy", "B. Organizations tag policy", "C. WAF web ACL", "D. KMS key policy"],
                "correct": 3,
                "explain": "The deciding resource is a KMS key. Its key policy is the primary authorization mechanism and must enable the principal or IAM delegation.",
            },
            {
                "q": "A company wants enhanced DDoS protection, cost-protection benefits, and access to the DDoS Response Team for critical applications. What should it use?",
                "options": ["A. AWS Shield Advanced", "B. AWS WAF managed SQL rules", "C. Amazon Macie", "D. Amazon Detective"],
                "correct": 0,
                "explain": "The deciding constraints are advanced DDoS support and cost protection. Those are Shield Advanced capabilities beyond Shield Standard.",
            },
        ],
    },
    11: {
        "visual_rules": [
            ("Translate objectives into architecture", "RPO limits acceptable data loss and drives replication or backup frequency; RTO limits outage duration and drives readiness and automation."),
            ("Do not confuse HA with DR", "Multi-AZ handles local infrastructure failure, while Regional disaster requirements need copies, capacity, routing, and runbooks in another Region."),
            ("Pay for readiness", "Backup and restore costs least but recovers slowest; pilot light, warm standby, and multi-site progressively reduce RTO while increasing steady cost."),
            ("Test the recovery path", "A DR design is incomplete until backups restore, dependencies start in order, data integrity is checked, and DNS or global routing fails over within objectives."),
        ],
        "scenarios": [
            {
                "tab": "Low Cost",
                "title": "Recover a noncritical application",
                "body": "A system can lose up to 24 hours of data and remain offline for a day, while minimizing steady-state cost. Use cross-Region backups with infrastructure as code and a tested restore runbook. Warm standby pays for running capacity that the RTO does not require, and multi-site is far more expensive.",
                "reason": ["Long RPO", "Long RTO", "Lowest standby cost"],
            },
            {
                "tab": "Minutes",
                "title": "Keep a scaled-down recovery stack",
                "body": "A business service needs a minutes-level RTO and very low RPO in a second Region, but cannot fund full duplicate capacity. Run a warm standby with replicated data and reduced application capacity, then scale on failover. Pilot light may need too much provisioning time, while multi-site pays for full active capacity.",
                "reason": ["Stack already live", "Scale on failover", "Replicated data"],
            },
            {
                "tab": "Near Zero",
                "title": "Serve from both Regions",
                "body": "A revenue platform requires near-zero RTO and RPO and can accept the highest operating cost and application complexity. Use multi-site active-active architecture with globally replicated data and health-based traffic steering. Backups, pilot light, and warm standby all require startup or scaling that violates the recovery objective.",
                "reason": ["Both sites active", "Immediate routing", "Highest readiness"],
            },
        ],
        "quiz": [
            {
                "q": "A workload may lose at most 15 minutes of committed data after a disaster. Which recovery metric states this requirement?",
                "options": ["A. Recovery point objective", "B. Recovery time objective", "C. Mean time between failures", "D. Mean time to repair"],
                "correct": 0,
                "explain": "The deciding constraint is acceptable data loss measured backward from disruption. That is the recovery point objective.",
            },
            {
                "q": "A company can tolerate a 24-hour outage and daily data loss, and it prioritizes the lowest ongoing DR cost. Which strategy is most suitable?",
                "options": ["A. Multi-site active-active", "B. Backup and restore", "C. Warm standby", "D. Full-capacity hot standby"],
                "correct": 1,
                "explain": "The deciding constraints are long RTO and RPO plus minimum cost. Backup and restore avoids continuously running a recovery environment.",
            },
            {
                "q": "Core databases replicate to a second Region, but application servers are created only after disaster declaration. Which DR strategy does this most closely describe?",
                "options": ["A. Backup and restore only", "B. Multi-site active-active", "C. Pilot light", "D. Warm standby"],
                "correct": 2,
                "explain": "The deciding pattern is always-on core data infrastructure with application capacity provisioned during recovery. That is pilot light.",
            },
            {
                "q": "A service requires near-zero recovery time and data loss across Regions, and cost is secondary. Which strategy best meets the objectives?",
                "options": ["A. Weekly snapshots", "B. Pilot light", "C. Warm standby at minimal scale", "D. Multi-site active-active"],
                "correct": 3,
                "explain": "The deciding constraints are near-zero RTO and RPO. Multi-site keeps full service capability active and routes around a failed Region.",
            },
            {
                "q": "An RDS Multi-AZ database survives an Availability Zone failure. Why might this still be insufficient for the stated Regional disaster requirement?",
                "options": ["A. Multi-AZ replicas remain in the same Region", "B. Multi-AZ never provides automatic failover", "C. Multi-AZ supports only read replicas", "D. Multi-AZ disables automated backups"],
                "correct": 0,
                "explain": "The deciding failure scope is an entire Region. Multi-AZ improves in-Region availability but does not by itself create a cross-Region recovery site.",
            },
        ],
    },
}


CAPTIONS = {
    1: "Network decisions become clear when every packet has a route, a state model, and the narrowest private path.",
    2: "Choose connectivity by topology, reachability scope, performance, encryption, and DNS direction.",
    3: "Separate request distribution, instance configuration, health replacement, and capacity scaling.",
    4: "Storage architecture starts with object, block, or file semantics before performance and lifecycle tuning.",
    5: "Select the data model first, then add availability, read scaling, global replication, and caching deliberately.",
    6: "Effective access is an allowed request that survives every policy ceiling and explicit deny.",
    7: "Protect keys and secrets, filter attacks at the right layer, and automate findings into response.",
    11: "Recovery objectives determine data-copy frequency, standby readiness, failover automation, and steady-state cost.",
}
