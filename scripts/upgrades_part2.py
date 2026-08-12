"""Lesson-specific visual coaching, scenarios, and quizzes for lessons 8-17."""


def _scenario(tab, title, body, reason):
    return {"tab": tab, "title": title, "body": body, "reason": reason}


def _question(q, options, correct, explain):
    return {"q": q, "options": options, "correct": correct, "explain": explain}


UPGRADES = {
    8: {
        "visual_rules": [
            ("Follow the invocation path", "Draw client, API Gateway or AppSync, Lambda, and each downstream service. Mark synchronous calls, asynchronous events, retries, and timeout boundaries."),
            ("Separate identity from permission", "Show Cognito user pools authenticating users, identity pools vending temporary AWS credentials, and IAM execution roles authorizing Lambda."),
            ("Budget every concurrency pool", "Annotate account concurrency, reserved concurrency, provisioned concurrency, event-source scaling, and downstream connection limits before choosing a Lambda design."),
            ("Match the API front door", "Use API Gateway for REST, HTTP, and WebSocket APIs; use AppSync when managed GraphQL, subscriptions, and offline synchronization drive the requirement."),
        ],
        "scenarios": [
            _scenario("API", "Bursting mobile checkout", "Constraint: a mobile checkout API has sharp bursts and must authenticate customers. Design: Cognito user pools issue tokens, API Gateway validates them, and Lambda writes idempotently to DynamoDB. Why alternatives fail: EC2 adds capacity management, while an identity pool alone does not provide a user directory.", ["User pool authenticates", "API Gateway validates JWT", "Idempotency absorbs retries"]),
            _scenario("GraphQL", "Live collaborative dashboard", "Constraint: web clients need GraphQL queries and near-real-time updates with minimal connection management. Design: AppSync subscriptions push changes and resolvers access DynamoDB or Lambda. Why alternatives fail: API Gateway REST needs custom fan-out, and polling wastes requests and increases latency.", ["AppSync manages GraphQL", "Subscriptions push updates", "Resolvers reach data"]),
            _scenario("Scale", "Database-safe Lambda ingestion", "Constraint: asynchronous jobs can spike beyond an RDS database's connection capacity. Design: buffer work in SQS, cap Lambda reserved concurrency, and use RDS Proxy. Why alternatives fail: provisioned concurrency reduces cold starts but does not cap database pressure; direct invocation removes buffering.", ["SQS smooths bursts", "Reserved concurrency caps load", "RDS Proxy pools connections"]),
        ],
        "quiz": [
            _question("A public mobile API needs sign-up, sign-in, password recovery, and JWT validation before Lambda runs. Which design has the least custom identity code?", ["A. Cognito user pool authorizer on API Gateway", "B. Cognito identity pool without a user pool", "C. Lambda execution role passed to users", "D. API keys stored in the mobile app"], 0, "A user pool supplies the user directory and tokens; API Gateway can validate those tokens before invoking Lambda."),
            _question("A Lambda consumer reads an SQS queue, but its downstream database supports only 40 concurrent writers. Which control most directly protects the database?", ["A. Increase Lambda memory", "B. Set reserved concurrency on the function", "C. Enable provisioned concurrency only", "D. Shorten the SQS visibility timeout"], 1, "Reserved concurrency places a hard ceiling on concurrent function executions; provisioned concurrency primarily controls readiness and cold starts."),
            _question("A web application needs managed GraphQL queries plus server-pushed updates when DynamoDB items change. Which service best fits with the least operations?", ["A. API Gateway REST API", "B. Application Load Balancer", "C. AWS AppSync", "D. CloudFront Functions"], 2, "AppSync provides managed GraphQL APIs, resolvers, and subscriptions for real-time updates."),
            _question("An asynchronous Lambda invocation fails repeatedly because a third-party endpoint is unavailable. Where should the team retain exhausted events for later analysis?", ["A. Lambda destination or dead-letter queue", "B. API Gateway stage cache", "C. Cognito identity pool", "D. Lambda layer"], 0, "After asynchronous retry attempts, Lambda can route failed events to an on-failure destination or a supported DLQ."),
            _question("A latency-sensitive Lambda has predictable morning traffic and unacceptable cold-start delays. Which feature prepares execution environments ahead of requests?", ["A. Reserved concurrency", "B. Provisioned concurrency", "C. SQS long polling", "D. API Gateway throttling"], 1, "Provisioned concurrency keeps initialized execution environments ready; reserved concurrency guarantees and limits capacity but does not pre-initialize it."),
        ],
    },
    9: {
        "visual_rules": [
            ("Separate image from runtime", "Trace source to ECR image, task or pod definition, and running workload. Image storage does not choose ECS, EKS, EC2, or Fargate."),
            ("Choose the control plane first", "Use ECS for AWS-native orchestration and EKS for Kubernetes compatibility; then choose EC2 nodes or Fargate as the compute layer."),
            ("Draw task networking", "For awsvpc mode, show each task receiving an ENI and security groups. Mark load balancer target groups, private subnets, and NAT or VPC endpoints."),
            ("Scale on the real bottleneck", "Distinguish service desired count, cluster capacity, pod replicas, and node capacity. Fargate removes node scaling but not application autoscaling."),
        ],
        "scenarios": [
            _scenario("ECS", "Simple microservice platform", "Constraint: a small team needs managed container orchestration without Kubernetes expertise. Design: ECS services on Fargate pull private images from ECR and register tasks with an ALB. Why alternatives fail: EKS adds Kubernetes administration, while plain EC2 lacks orchestration.", ["ECS minimizes control work", "Fargate removes nodes", "ECR stores images"]),
            _scenario("EKS", "Portable Kubernetes workloads", "Constraint: an organization requires Kubernetes APIs, Helm charts, and familiar ecosystem tooling. Design: EKS supplies the managed control plane with managed node groups or Fargate profiles. Why alternatives fail: ECS does not expose Kubernetes APIs, and self-managed Kubernetes increases operational burden.", ["EKS preserves Kubernetes", "Nodes or Fargate run pods", "AWS manages control plane"]),
            _scenario("Registry", "Private image delivery", "Constraint: deployments need private, scanned, versioned images close to AWS compute. Design: push immutable tags to ECR, enable scanning, and grant task execution roles pull access. Why alternatives fail: S3 is not an OCI registry, and public registries weaken private access control.", ["ECR is managed registry", "Execution role pulls", "Immutable tags reduce drift"]),
        ],
        "quiz": [
            _question("A team wants to run ECS tasks without patching instances or managing cluster capacity providers. Which compute choice best satisfies the requirement?", ["A. ECS on Fargate", "B. ECS on dedicated hosts", "C. EKS self-managed nodes", "D. Docker directly on EC2"], 0, "Fargate provides serverless compute for ECS tasks, removing EC2 host provisioning and patching."),
            _question("A company must reuse Helm charts and Kubernetes operators after moving to AWS. Which managed orchestration service is the appropriate target?", ["A. Amazon ECS", "B. Amazon EKS", "C. AWS Batch only", "D. Elastic Beanstalk worker tier"], 1, "EKS exposes a managed Kubernetes control plane compatible with Kubernetes tooling and APIs."),
            _question("An ECS task in awsvpc network mode needs distinct inbound rules from other tasks. Which resource can be assigned directly to that task networking?", ["A. A security group on its ENI", "B. An IAM user access key", "C. A CloudFront origin policy", "D. An ECR lifecycle rule"], 0, "awsvpc mode gives each task an elastic network interface to which security groups can be attached."),
            _question("Private ECS tasks must pull ECR images without traversing a NAT gateway. Which design keeps image access on the AWS network?", ["A. ECR API and DKR interface endpoints plus S3 gateway endpoint", "B. Internet gateway on each task ENI", "C. CloudFront distribution for ECR", "D. Route 53 Resolver outbound endpoint"], 0, "Private ECR pulls use ECR interface endpoints and the S3 gateway endpoint for image layers."),
            _question("An ECS service behind an ALB must maintain six healthy copies during deployments and failures. Which setting represents that application capacity?", ["A. ECR repository count", "B. ECS service desired count", "C. Number of EKS control planes", "D. Docker image layer count"], 1, "The ECS service scheduler maintains the desired task count and replaces unhealthy tasks."),
        ],
    },
    10: {
        "visual_rules": [
            ("Name delivery semantics", "Label queues and buses with ordering, duplication, retention, retry, and acknowledgement behavior. Standard SQS is at-least-once; FIFO adds ordered message groups and deduplication."),
            ("Distinguish queue from fan-out", "Use SQS when consumers pull and buffer work, SNS when publishers push one message to many subscribers, and combine them for durable fan-out."),
            ("Map event intent", "EventBridge routes application and SaaS events by content; Step Functions coordinates stateful workflows, branching, retries, waits, and compensation."),
            ("Place failure stores deliberately", "Draw source-queue DLQs, subscription redrive, EventBridge DLQs, and workflow catches at the component that owns retry exhaustion."),
        ],
        "scenarios": [
            _scenario("Fan-out", "Independent order processors", "Constraint: billing, fulfillment, and analytics must each process every order independently and survive downtime. Design: publish to SNS with a separate SQS subscription per consumer. Why alternatives fail: one shared queue load-balances messages instead of copying them, and direct calls couple availability.", ["SNS copies each event", "SQS buffers per consumer", "Policies isolate access"]),
            _scenario("Workflow", "Long-running approval flow", "Constraint: a process waits for approval, branches on risk, and retries selected steps for days. Design: Step Functions Standard orchestrates services with waits, choices, and error handling. Why alternatives fail: Lambda cannot run for days, and SQS alone does not model workflow state.", ["Standard supports long runs", "State machine records progress", "Retries are per state"]),
            _scenario("Routing", "Cross-application business events", "Constraint: many targets need only events matching attributes such as source and detail type. Design: EventBridge rules filter events and route them to targets, with archives or DLQs where needed. Why alternatives fail: SNS filtering is subscription-oriented, and SQS is not an event bus.", ["Rules match content", "Bus decouples producers", "Targets receive selected events"]),
        ],
        "quiz": [
            _question("Three services must each receive every order event and process at different rates without losing messages during outages. Which architecture is best?", ["A. One shared standard SQS queue", "B. SNS topic with one SQS queue per service", "C. Direct synchronous Lambda calls", "D. One Step Functions Express execution"], 1, "SNS provides fan-out, while a separate SQS queue gives every service an independent durable backlog."),
            _question("A payment processor requires ordered messages per customer while different customers can run in parallel. Which SQS feature provides this behavior?", ["A. Standard queue delay seconds", "B. FIFO queue message group IDs", "C. Queue access policy", "D. Dead-letter redrive allow policy"], 1, "FIFO message groups preserve order within each group while allowing multiple groups to be processed concurrently."),
            _question("A workflow can run for several hours and needs an auditable execution history, human waits, and exactly-once workflow execution semantics. Which service fits?", ["A. Step Functions Standard", "B. Step Functions Express", "C. SNS FIFO only", "D. SQS standard queue only"], 0, "Standard Workflows support long-running, auditable executions and exactly-once workflow execution semantics."),
            _question("An SQS consumer repeatedly fails a poison message and blocks useful retries. What configuration isolates it after a bounded receive count?", ["A. Configure a DLQ and maxReceiveCount", "B. Increase message retention only", "C. Disable long polling", "D. Add an SNS message filter"], 0, "The redrive policy moves a message to the DLQ after its receive count exceeds maxReceiveCount."),
            _question("A SaaS application emits events that must route to targets according to fields in each JSON event, with minimal custom routing code. Choose the service.", ["A. Amazon EventBridge", "B. Amazon EBS", "C. Amazon MQ client library only", "D. S3 Transfer Acceleration"], 0, "EventBridge event patterns filter structured events and rules route matching events to supported targets."),
        ],
    },
    12: {
        "visual_rules": [
            ("Separate content from packets", "CloudFront caches HTTP content at edge locations; Global Accelerator moves TCP or UDP traffic over the AWS global network to healthy regional endpoints."),
            ("Trace DNS decisions", "Show Route 53 record type, routing policy, health check, TTL, and alias target. DNS steers clients but does not proxy established connections."),
            ("Mark cache-key boundaries", "Annotate which headers, cookies, and query strings enter the CloudFront cache key and which are only forwarded to the origin."),
            ("Design origin protection", "Keep S3 origins private with origin access control and restrict custom origins where possible; pair edge delivery with WAF and TLS requirements."),
        ],
        "scenarios": [
            _scenario("CDN", "Private global media site", "Constraint: users worldwide need low-latency downloads from a private S3 bucket. Design: CloudFront caches objects and uses origin access control to sign origin requests. Why alternatives fail: S3 website endpoints cannot use OAC, and Route 53 alone does not cache content.", ["CloudFront caches objects", "OAC protects S3", "HTTPS terminates at edge"]),
            _scenario("Accelerator", "Global gaming endpoint", "Constraint: a latency-sensitive TCP game needs static anycast IPs and rapid regional failover. Design: Global Accelerator sends traffic over the AWS backbone to healthy ALB or NLB endpoints. Why alternatives fail: CloudFront is HTTP-content oriented, while DNS failover depends on resolver caching.", ["Anycast IPs stay stable", "Backbone reduces internet path", "Health shifts endpoints"]),
            _scenario("DNS", "Regional active-passive site", "Constraint: a web name should use the primary region unless its endpoint is unhealthy. Design: Route 53 failover alias records and health evaluation select the secondary. Why alternatives fail: weighted routing is not inherently active-passive, and latency routing optimizes latency rather than priority.", ["Failover expresses priority", "Health controls answers", "Alias targets AWS resource"]),
        ],
        "quiz": [
            _question("A company serves private S3 objects globally and wants users unable to bypass the CDN by calling S3 directly. Which configuration is recommended?", ["A. CloudFront with origin access control and restrictive bucket policy", "B. Public S3 website endpoint with signed cookies", "C. Route 53 latency record only", "D. Global Accelerator endpoint to S3"], 0, "OAC lets CloudFront sign S3 origin requests while the bucket policy denies direct public access."),
            _question("A global TCP application needs two fixed anycast IP addresses and fast endpoint failover unaffected by DNS caches. Which service should front it?", ["A. CloudFront", "B. Global Accelerator", "C. Route 53 geolocation routing", "D. S3 Multi-Region Access Point"], 1, "Global Accelerator supplies static anycast IPs and routes new connections to healthy endpoints over the AWS global network."),
            _question("Users should resolve to the AWS Region offering the lowest measured network latency, and DNS-based steering is acceptable. Which Route 53 policy fits?", ["A. Weighted", "B. Latency-based", "C. Geolocation", "D. Multivalue answer without health checks"], 1, "Latency-based routing chooses the configured resource in the Region that provides the lowest latency measurement."),
            _question("A CloudFront distribution has poor cache hit ratio because an unused unique request header is in the cache key. What change most directly improves reuse?", ["A. Remove the header from the cache policy key", "B. Lower the minimum TTL to zero", "C. Add more Route 53 records", "D. Enable Global Accelerator"], 0, "Values included in the cache key create cache variants; removing an irrelevant unique header allows requests to share objects."),
            _question("A company wants to direct 10% of DNS responses to a new endpoint and 90% to the old endpoint during a gradual release. Which policy is designed for this?", ["A. Failover", "B. Weighted", "C. Geoproximity only", "D. IP-based without CIDRs"], 1, "Weighted records distribute DNS responses according to relative weights and are commonly used for controlled traffic shifts."),
        ],
    },
    13: {
        "visual_rules": [
            ("Classify velocity and latency", "Separate real-time stream processing, near-real-time delivery, interactive S3 queries, ETL catalogs, warehouse analytics, and transactional workloads."),
            ("Show shards and partitions", "For Kinesis, annotate shard throughput and partition keys; for S3 analytics, show partitioned prefixes and columnar formats that reduce scans."),
            ("Distinguish delivery from processing", "Data Firehose buffers, transforms optionally, and delivers to destinations; Kinesis Data Streams retains ordered records for custom consumers."),
            ("Place the metadata layer", "Glue crawlers and the Data Catalog describe datasets; Athena queries S3 in place, while Redshift stores and optimizes warehouse data."),
        ],
        "scenarios": [
            _scenario("Streaming", "Replayable telemetry stream", "Constraint: several consumers need ordered device telemetry and must replay records after failures. Design: Kinesis Data Streams partitions by device and retains records for independent consumers. Why alternatives fail: Firehose is delivery-focused, and SQS does not provide the same shard-based replay stream.", ["Partition key preserves order", "Consumers read independently", "Retention enables replay"]),
            _scenario("Lake", "Serverless log investigation", "Constraint: analysts sporadically query years of logs in S3 without loading a warehouse. Design: catalog partitioned Parquet data with Glue and query it using Athena. Why alternatives fail: Redshift adds provisioned warehouse concerns, and RDS is not optimized for lake scans.", ["Athena queries S3", "Glue supplies schema", "Parquet reduces bytes scanned"]),
            _scenario("Warehouse", "Repeated BI joins", "Constraint: many users run frequent complex joins and aggregations over curated enterprise data. Design: load a dimensional model into Redshift and scale or isolate workloads appropriately. Why alternatives fail: Athena can be less predictable for repeated high-concurrency BI, and DynamoDB lacks relational joins.", ["Redshift is columnar", "MPP accelerates analytics", "Workload controls concurrency"]),
        ],
        "quiz": [
            _question("Multiple applications must independently consume and replay ordered clickstream records for up to several days. Which ingestion service best meets the need?", ["A. Kinesis Data Streams", "B. Data Firehose only", "C. SNS without queues", "D. AWS Glue crawler"], 0, "Kinesis Data Streams retains records and supports multiple consumers; partition keys order records within a shard."),
            _question("A company wants a fully managed service to buffer streaming records and deliver compressed files to S3 with almost no consumer code. What should it use?", ["A. Kinesis Data Streams enhanced fan-out", "B. Amazon Data Firehose", "C. Amazon Athena", "D. Redshift Spectrum only"], 1, "Data Firehose manages buffering, optional conversion or transformation, and delivery to destinations such as S3."),
            _question("Athena queries scan too much S3 data and cost too much. Which two data-layout changes provide the most direct improvement?", ["A. Convert to Parquet and partition by common predicates", "B. Convert to XML and merge all dates", "C. Replicate data to more Regions", "D. Increase Kinesis shard count"], 0, "Columnar Parquet reads needed columns, and partitions let Athena skip files outside common filter predicates."),
            _question("Analysts need a shared schema registry for S3 datasets discovered automatically and queried by Athena. Which service provides this metadata?", ["A. AWS Glue Data Catalog", "B. CloudWatch Logs Insights", "C. Amazon ECR", "D. AWS Config aggregator"], 0, "Glue crawlers can infer schemas and populate the Glue Data Catalog, which Athena uses for table metadata."),
            _question("A BI platform runs frequent complex joins over terabytes of curated data and needs a columnar massively parallel warehouse. Which service is designed for it?", ["A. Amazon Redshift", "B. Amazon DynamoDB", "C. Amazon SQS", "D. AWS DataSync"], 0, "Redshift is a columnar MPP data warehouse designed for large-scale analytic queries and joins."),
        ],
    },
    14: {
        "visual_rules": [
            ("Match mover to source", "Use DMS for databases, DataSync for online file or object transfer, MGN for server replication, Snow devices for offline bulk data, and Transfer Family for managed partner protocols."),
            ("Separate migration from access", "A one-time or recurring copy is different from hybrid low-latency access. Storage Gateway presents file, volume, or tape interfaces backed by AWS storage."),
            ("Mark downtime and change flow", "Draw initial load, ongoing replication, validation, cutover, rollback, and the point applications stop writing to the source."),
            ("Quantify the network", "Compare dataset size, available bandwidth, migration window, encryption, Direct Connect or VPN, and whether an offline Snow workflow is faster."),
        ],
        "scenarios": [
            _scenario("Database", "Low-downtime database move", "Constraint: a production database must move with only a brief cutover. Design: DMS performs full load plus change data capture, with Schema Conversion Tool where engines differ. Why alternatives fail: DataSync copies files, and MGN replicates servers rather than database changes.", ["DMS moves data", "CDC follows changes", "SCT converts schema"]),
            _scenario("Files", "Recurring NAS transfer", "Constraint: an on-premises NFS share must synchronize nightly to S3 with verification and bandwidth controls. Design: DataSync agents perform incremental scheduled transfers. Why alternatives fail: Storage Gateway exposes ongoing hybrid access, while Snow devices are offline and not nightly synchronization.", ["DataSync handles files", "Incremental copies save bandwidth", "Verification checks transfer"]),
            _scenario("Offline", "Petabyte migration with weak link", "Constraint: petabytes must reach AWS while the WAN would take months. Design: use an appropriate AWS Snow device workflow and track encrypted shipment. Why alternatives fail: DataSync remains bandwidth-bound, and Transfer Family does not create physical transport capacity.", ["Snow bypasses WAN", "Data stays encrypted", "Capacity drives device choice"]),
        ],
        "quiz": [
            _question("A PostgreSQL database must migrate to Amazon Aurora with minimal downtime while source writes continue until cutover. Which service captures ongoing changes?", ["A. AWS DMS with CDC", "B. AWS DataSync", "C. AWS Snowball Edge only", "D. S3 Transfer Acceleration"], 0, "DMS change data capture replicates ongoing source changes after or during the initial full load."),
            _question("An enterprise needs scheduled incremental transfers from an on-premises NFS server to S3, including integrity verification. Which service is purpose-built?", ["A. AWS DataSync", "B. AWS MGN", "C. AWS Glue", "D. Amazon AppFlow"], 0, "DataSync is an online transfer service for file and object storage with scheduling, verification, and network controls."),
            _question("Hundreds of VMware servers must be continuously replicated to AWS and launched as EC2 instances during cutover. Which migration service fits?", ["A. AWS Application Migration Service", "B. AWS Database Migration Service", "C. AWS Transfer Family", "D. File Gateway"], 0, "AWS MGN performs block-level server replication and orchestrates test and cutover launches into EC2."),
            _question("External partners must upload files over SFTP into Amazon S3 while AWS manages the protocol endpoint. Which service should be selected?", ["A. AWS Transfer Family", "B. AWS DataSync agent", "C. Volume Gateway", "D. Kinesis Data Streams"], 0, "Transfer Family provides managed SFTP, FTPS, FTP, and AS2 endpoints backed by S3 or EFS."),
            _question("On-premises applications need an NFS file share with local caching while objects are durably stored in S3. Which hybrid service meets this pattern?", ["A. S3 File Gateway", "B. AWS DMS", "C. Snowcone import job", "D. ECR pull-through cache"], 0, "S3 File Gateway exposes NFS or SMB with local caching and stores files as objects in S3."),
        ],
    },
    15: {
        "visual_rules": [
            ("Assign each evidence source", "CloudWatch holds metrics, logs, alarms, and events; CloudTrail records API activity; Config evaluates resource configuration and history."),
            ("Separate observe from act", "Draw the alarm or compliance signal, EventBridge routing, automation target, approval boundary, and rollback path."),
            ("Prefer managed fleet access", "Use Systems Manager Session Manager, Run Command, Patch Manager, and State Manager instead of inbound SSH and manually maintained bastions where supported."),
            ("Show governance hierarchy", "Map organizations, OUs, accounts, Control Tower guardrails, SCP boundaries, Config rules, and CloudFormation StackSets without treating SCPs as grants."),
        ],
        "scenarios": [
            _scenario("Audit", "Who changed the security group?", "Constraint: investigators need the identity, time, source, and API call that modified a security group. Design: search CloudTrail event history or a centralized trail. Why alternatives fail: CloudWatch metrics show behavior, and Config history shows configuration change but is not the primary API caller record.", ["CloudTrail records API", "Identity appears in event", "Central trails aid audit"]),
            _scenario("Fleet", "No-ingress server administration", "Constraint: operators must access private EC2 instances without opening port 22 or distributing SSH keys. Design: use SSM Session Manager with managed-instance permissions and connectivity. Why alternatives fail: a bastion still needs inbound access, and CloudFormation is not an interactive shell.", ["Session Manager avoids inbound", "IAM controls sessions", "Logs support audit"]),
            _scenario("Landing zone", "Governed multi-account growth", "Constraint: new accounts need repeatable baselines, centralized logging, and preventive or detective controls. Design: Control Tower establishes the landing zone and guardrails, with Organizations and account factory. Why alternatives fail: Config alone does not provision accounts, and CloudFormation alone lacks landing-zone governance.", ["Control Tower builds baseline", "Guardrails govern OUs", "Account factory standardizes"]),
        ],
        "quiz": [
            _question("Security asks which principal called DeleteBucket and from which IP address yesterday. Which AWS service provides the authoritative API activity event?", ["A. AWS CloudTrail", "B. Amazon CloudWatch metrics", "C. AWS Config rule evaluation", "D. Systems Manager Inventory"], 0, "CloudTrail management events record API calls with identity, timestamp, source IP, request, and response details."),
            _question("A team must detect that an S3 bucket became public and view how its configuration changed over time. Which service directly tracks this state?", ["A. AWS Config", "B. AWS CloudTrail Insights only", "C. CloudWatch Application Signals", "D. Systems Manager Parameter Store"], 0, "Config records resource configuration history and evaluates resources against compliance rules."),
            _question("Administrators need shell access to private EC2 instances without inbound ports, bastions, or SSH keys. Which Systems Manager feature is designed for this?", ["A. Session Manager", "B. Distributor", "C. OpsCenter only", "D. CloudFormation drift detection"], 0, "Session Manager brokers IAM-controlled sessions through the SSM service without requiring inbound SSH."),
            _question("A CloudFormation stack resource was manually modified, and operators need to identify divergence from its template. Which feature should they run?", ["A. CloudFormation drift detection", "B. CloudTrail log file validation", "C. CloudWatch anomaly detection", "D. Control Tower account enrollment"], 0, "Drift detection compares supported resources' actual configuration with expected CloudFormation properties."),
            _question("A company needs a governed multi-account landing zone with account vending and preconfigured controls. Which service provides the highest-level solution?", ["A. AWS Control Tower", "B. Amazon CloudWatch", "C. AWS Systems Manager", "D. AWS Artifact"], 0, "Control Tower orchestrates a landing zone, account factory, centralized controls, and guardrails using underlying AWS services."),
        ],
    },
    16: {
        "visual_rules": [
            ("Optimize the billing dimension", "Identify whether cost is driven by provisioned time, requests, bytes stored, bytes scanned, data transfer, NAT processing, IOPS, or licensed cores."),
            ("Commit only after baselining", "Use Savings Plans or Reserved Instances for stable compute baselines; keep burst and uncertain demand on flexible pricing."),
            ("Tier by access evidence", "Apply S3 lifecycle rules for known patterns or Intelligent-Tiering for uncertain patterns, while including retrieval fees and minimum storage durations."),
            ("Treat architecture as cost control", "Show cache hits, compression, right-sized resources, Graviton compatibility, serverless idle behavior, and same-AZ or endpoint paths that avoid needless transfer."),
        ],
        "scenarios": [
            _scenario("Compute", "Stable baseline with bursts", "Constraint: compute has a steady year-round baseline plus unpredictable peaks. Design: cover the measured baseline with a suitable Savings Plan and run peaks on demand or Spot where interruptible. Why alternatives fail: committing to peak wastes money, and Spot is unsafe for noninterruptible baseline capacity.", ["Commit only baseline", "On-Demand handles uncertainty", "Spot fits interruption"]),
            _scenario("Storage", "Unknown object access", "Constraint: millions of long-lived objects have changing, unpredictable access frequency. Design: S3 Intelligent-Tiering moves eligible objects among access tiers automatically. Why alternatives fail: rigid lifecycle dates can misclassify changing access, and Standard keeps every object at the higher frequent-access rate.", ["Monitoring learns access", "No retrieval fee for access tiers", "Archive tiers are optional"]),
            _scenario("Network", "Expensive private downloads", "Constraint: private instances download large S3 datasets through NAT gateways, creating processing charges. Design: add an S3 gateway endpoint and route S3 traffic privately. Why alternatives fail: a larger NAT gateway does not reduce per-byte processing, and an internet gateway cannot serve private instances directly.", ["Gateway endpoint avoids NAT", "S3 route stays private", "No endpoint hourly charge"]),
        ],
        "quiz": [
            _question("A company has a predictable minimum EC2 spend for three years but may change instance families and Regions. Which discount offers the broadest compute flexibility?", ["A. Compute Savings Plan", "B. Standard Reserved Instance", "C. Dedicated Host reservation only", "D. Spot Instance"], 0, "Compute Savings Plans apply across eligible EC2 families, sizes, operating systems, tenancy, and Regions, plus Fargate and Lambda."),
            _question("Private subnets transfer terabytes to S3 through a NAT gateway every day. Which change most directly removes NAT data-processing charges for this traffic?", ["A. Add an S3 gateway VPC endpoint", "B. Buy a NAT gateway reservation", "C. Add a second internet gateway", "D. Enable S3 Transfer Acceleration"], 0, "An S3 gateway endpoint routes supported S3 traffic without traversing the NAT gateway and has no hourly endpoint charge."),
            _question("Objects have unpredictable access that changes over time, and operations wants automatic tiering without writing lifecycle timing guesses. Which class fits?", ["A. S3 Intelligent-Tiering", "B. S3 Standard only", "C. S3 One Zone-IA for every object", "D. S3 Glacier Deep Archive immediately"], 0, "Intelligent-Tiering monitors access and automatically moves eligible objects among tiers while preserving millisecond access in online tiers."),
            _question("A fault-tolerant batch fleet can lose workers and resume jobs from checkpoints. Which EC2 purchasing option usually offers the deepest discount?", ["A. Spot Instances", "B. On-Demand Capacity Reservations", "C. Dedicated Hosts", "D. Standard On-Demand only"], 0, "Spot uses spare EC2 capacity at steep discounts but can be interrupted, making checkpointed fault-tolerant batch a strong fit."),
            _question("Athena costs increased after analysts began querying raw JSON logs across all dates. Which redesign lowers scanned bytes without changing the query service?", ["A. Store partitioned Parquet and filter partitions", "B. Copy JSON through a NAT gateway", "C. Increase CloudWatch retention", "D. Purchase EC2 Reserved Instances"], 0, "Athena charges primarily by bytes scanned; columnar compression and partition pruning directly reduce scanned data."),
        ],
    },
    17: {
        "visual_rules": [
            ("Translate words into constraints", "Underline availability, durability, latency, throughput, recovery, operations, security, and cost requirements before selecting any service."),
            ("Build the data path", "Sketch entry, identity, compute, state, asynchronous boundaries, observability, and failure destinations; then test every hop against the stated constraints."),
            ("Eliminate by violated requirement", "Reject answers that break an explicit constraint, add unrequested operations, confuse authentication with authorization, or optimize a secondary concern."),
            ("Prefer reversible decisions", "When two answers work, favor managed, loosely coupled, multi-AZ, observable designs that scale independently and minimize undifferentiated operations."),
        ],
        "scenarios": [
            _scenario("Pattern", "Resilient web transaction", "Constraint: a public workload must remain available through an AZ failure and absorb bursts. Design: Route 53 and an ALB front Auto Scaling instances across AZs, with Multi-AZ data and SQS for asynchronous work. Why alternatives fail: one large instance is a single failure domain, and synchronous chaining spreads failure.", ["Multi-AZ removes one fault", "Auto Scaling replaces capacity", "Queues isolate bursts"]),
            _scenario("Recovery", "Choosing DR by objective", "Constraint: the business supplies strict RTO and RPO rather than asking for maximum availability at any cost. Design: map backup/restore, pilot light, warm standby, or multi-site to those objectives and test recovery. Why alternatives fail: backups may miss a short RTO, while active-active can overspend for relaxed objectives.", ["RPO limits lost data", "RTO limits outage", "Testing validates recovery"]),
            _scenario("Exam", "Resolving two plausible answers", "Constraint: two architectures appear technically possible under time pressure. Design: compare each against every superlative and explicit constraint, then choose the simplest managed option satisfying all. Why alternatives fail: keyword matching ignores trade-offs, and adding services can violate cost or operations requirements.", ["Read the final ask", "Honor every constraint", "Managed usually lowers ops"]),
        ],
        "quiz": [
            _question("A question asks for the least operationally intensive highly available relational database. Which clue should dominate when several technically valid designs appear?", ["A. Choose the managed Multi-AZ option satisfying all constraints", "B. Choose the design with the most services", "C. Build manual replication on EC2", "D. Ignore the operational requirement"], 0, "The explicit superlative is decisive: a managed Multi-AZ database generally minimizes administration while meeting availability."),
            _question("A workload can tolerate hours of recovery and up to one day of data loss. Which disaster-recovery strategy is usually the most cost-effective starting point?", ["A. Backup and restore", "B. Multi-site active-active", "C. Warm standby at full production scale", "D. Synchronous writes to three Regions"], 0, "Relaxed RTO and RPO commonly permit backup and restore, which has lower steady-state cost than continuously running environments."),
            _question("An order API must respond quickly even when fulfillment is slow or unavailable. Which general architecture pattern best isolates the user request path?", ["A. Put durable messaging between order acceptance and fulfillment", "B. Call every fulfillment step synchronously", "C. Increase DNS TTL", "D. Store orders only in instance memory"], 0, "A durable queue decouples availability and rate, allowing the API to acknowledge accepted work without waiting for fulfillment."),
            _question("Two answers meet functional needs, but one uses self-managed clusters and the other a managed service with equivalent controls. The stem says minimize operations. Choose what?", ["A. The managed service", "B. The self-managed cluster", "C. Whichever answer is longer", "D. The option with more EC2 instances"], 0, "When constraints are otherwise equal, the managed service directly satisfies the requirement to minimize operational overhead."),
            _question("A design is Multi-AZ but has synchronous dependencies on one regional external endpoint. What exam habit most likely reveals this hidden availability risk?", ["A. Trace the full request and failure path", "B. Count only the number of AZs", "C. Select the newest AWS service", "D. Ignore dependencies outside compute"], 0, "End-to-end tracing exposes dependencies whose failure can defeat otherwise redundant compute and storage layers."),
        ],
    },
}


CAPTIONS = {
    8: "Serverless decisions: identity, invocation, concurrency, and managed APIs.",
    9: "Container decisions: registry, orchestrator, compute layer, and task networking.",
    10: "Messaging decisions: buffering, fan-out, event routing, workflow, and failure handling.",
    12: "Global delivery decisions: DNS steering, edge caching, acceleration, and origin protection.",
    13: "Analytics decisions: ingest velocity, delivery, catalog, query engine, and warehouse.",
    14: "Migration decisions: source type, transfer path, downtime, bandwidth, and hybrid access.",
    15: "Operations decisions: observe, audit, evaluate, automate, and govern at scale.",
    16: "Cost decisions: measure the billing driver, right-size, tier, commit, and verify.",
    17: "Exam decisions: extract constraints, trace failure paths, eliminate, and choose.",
}
