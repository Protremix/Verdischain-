     1	import 'package:flutter/material.dart';
     2	import 'package:flutter/services.dart';
     3	import 'package:flutter_riverpod/flutter_riverpod.dart';
     4	
     5	import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
     6	import 'confirmation_page.dart';
     7	import 'qr_scanner_page.dart';
     8	import 'transactions_providers.dart';
     9	import 'utils/address_validator.dart';
    10	import 'widgets/fee_estimate.dart';
    11	
    12	/// Send Page screen for initiating transfers on Verdis Network
    13	class SendPage extends ConsumerStatefulWidget {
    14	
    15	  const SendPage({
    16	    super.key,
    17	    this.initialRecipient,
    18	    this.initialAmount,
    19	  });
    20	  final String? initialRecipient;
    21	  final double? initialAmount;
    22	
    23	  @override
    24	  ConsumerState<SendPage> createState() => _SendPageState();
    25	}
    26	
    27	class _SendPageState extends ConsumerState<SendPage> {
    28	  late final TextEditingController _recipientController;
    29	  late final TextEditingController _amountController;
    30	  final _formKey = GlobalKey<FormState>();
    31	
    32	  String? _addressError;
    33	
    34	  @override
    35	  void initState() {
    36	    super.initState();
    37	    _recipientController =
    38	        TextEditingController(text: widget.initialRecipient ?? '');
    39	    _amountController = TextEditingController(
    40	        text: widget.initialAmount != null ? widget.initialAmount.toString() : '',);
    41	  }
    42	
    43	  @override
    44	  void dispose() {
    45	    _recipientController.dispose();
    46	    _amountController.dispose();
    47	    super.dispose();
    48	  }
    49	
    50	  void _onScanQr() async {
    51	    final scannedResult = await Navigator.push<String>(
    52	      context,
    53	      MaterialPageRoute(builder: (context) => const QrScannerPage()),
    54	    );
    55	
    56	    if (scannedResult != null && scannedResult.isNotEmpty) {
    57	      setState(() {
    58	        _recipientController.text = scannedResult;
    59	        _addressError = AddressValidator.getValidationError(scannedResult);
    60	      });
    61	    }
    62	  }
    63	
    64	  void _onPasteRecipient() async {
    65	    final clipboardData = await Clipboard.getData('text/plain');
    66	    if (clipboardData != null && clipboardData.text != null) {
    67	      final text = clipboardData.text!.trim();
    68	      setState(() {
    69	        _recipientController.text = text;
    70	        _addressError = AddressValidator.getValidationError(text);
    71	      });
    72	    }
    73	  }
    74	
    75	  void _onSetMaxAmount(double availableBalance, double estimatedFee) {
    76	    final maxAmount = (availableBalance - estimatedFee).clamp(0.0, availableBalance);
    77	    setState(() {
    78	      _amountController.text = maxAmount.toStringAsFixed(4);
    79	    });
    80	  }
    81	
    82	  void _onSubmitSend() {
    83	    final recipient = _recipientController.text.trim();
    84	    final amountText = _amountController.text.trim();
    85	    final amount = double.tryParse(amountText) ?? 0.0;
    86	    final balance = ref.read(userWalletBalanceProvider);
    87	
    88	    final error = AddressValidator.getValidationError(recipient);
    89	    if (error != null) {
    90	      setState(() {
    91	        _addressError = error;
    92	      });
    93	      return;
    94	    }
    95	
    96	    if (amount <= 0) {
    97	      ScaffoldMessenger.of(context).showSnackBar(
    98	        const SnackBar(content: Text('Please enter a valid amount greater than 0')),
    99	      );
   100	      return;
   101	    }
   102	
   103	    if (amount > balance) {
   104	      ScaffoldMessenger.of(context).showSnackBar(
   105	        SnackBar(content: Text('Amount exceeds available balance (${balance.toStringAsFixed(2)} VRDX)')),
   106	      );
   107	      return;
   108	    }
   109	
   110	    final speed = ref.read(selectedFeeSpeedProvider);
   111	
   112	    // Show Confirmation dialog or navigate to ConfirmationPage
   113	    Navigator.push(
   114	      context,
   115	      MaterialPageRoute(
   116	        builder: (context) => ConfirmationPage(
   117	          recipient: recipient,
   118	          amount: amount,
   119	          feeSpeed: speed,
   120	        ),
   121	      ),
   122	    );
   123	  }
   124	
   125	  @override
   126	  Widget build(BuildContext context) {
   127	    final theme = Theme.of(context);
   128	    final balance = ref.watch(userWalletBalanceProvider);
   129	    final selectedSpeed = ref.watch(selectedFeeSpeedProvider);
   130	
   131	    final currentAmount = double.tryParse(_amountController.text) ?? 0.0;
   132	    final feeAsync = ref.watch(feeEstimateProvider({
   133	      'recipient': _recipientController.text,
   134	      'amount': currentAmount,
   135	      'speed': selectedSpeed,
   136	    }),);
   137	    final fee = feeAsync.valueOrNull ?? 0.0012;
   138	
   139	    return Scaffold(
   140	      appBar: AppBar(
   141	        title: const Text('Send VRDX'),
   142	        actions: [
   143	          IconButton(
   144	            icon: const Icon(Icons.qr_code_scanner),
   145	            tooltip: 'Scan QR',
   146	            onPressed: _onScanQr,
   147	          ),
   148	        ],
   149	      ),
   150	      body: SafeArea(
   151	        child: SingleChildScrollView(
   152	          padding: const EdgeInsets.all(20.0),
   153	          child: Form(
   154	            key: _formKey,
   155	            child: Column(
   156	              crossAxisAlignment: CrossAxisAlignment.start,
   157	              children: [
   158	                // Balance Banner Card
   159	                VerdisCard(
   160	                  padding: const EdgeInsets.all(16),
   161	                  child: Row(
   162	                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
   163	                    children: [
   164	                      Column(
   165	                        crossAxisAlignment: CrossAxisAlignment.start,
   166	                        children: [
   167	                          Text(
   168	                            'Available Balance',
   169	                            style: theme.textTheme.bodySmall?.copyWith(
   170	                              color: theme.colorScheme.onSurfaceVariant,
   171	                            ),
   172	                          ),
   173	                          const SizedBox(height: 4),
   174	                          Text(
   175	                            '${balance.toStringAsFixed(2)} VRDX',
   176	                            style: theme.textTheme.headlineSmall?.copyWith(
   177	                              color: theme.colorScheme.primary,
   178	                              fontWeight: FontWeight.bold,
   179	                            ),
   180	                          ),
   181	                        ],
   182	                      ),
   183	                      Icon(
   184	                        Icons.account_balance_wallet_rounded,
   185	                        color: theme.colorScheme.primary,
   186	                        size: 32,
   187	                      ),
   188	                    ],
   189	                  ),
   190	                ),
   191	                const SizedBox(height: 24),
   192	
   193	                // Recipient Address Input
   194	                Text(
   195	                  'Recipient Address',
   196	                  style: theme.textTheme.titleSmall?.copyWith(
   197	                    fontWeight: FontWeight.bold,
   198	                  ),
   199	                ),
   200	                const SizedBox(height: 8),
   201	                TextFormField(
   202	                  controller: _recipientController,
   203	                  onChanged: (val) {
   204	                    setState(() {
   205	                      _addressError = AddressValidator.getValidationError(val);
   206	                    });
   207	                  },
   208	                  style: const TextStyle(fontFamily: 'monospace', fontSize: 13),
   209	                  decoration: InputDecoration(
   210	                    hintText: 'Enter Verdis SS58 address',
   211	                    errorText: _addressError,
   212	                    suffixIcon: Row(
   213	                      mainAxisSize: MainAxisSize.min,
   214	                      children: [
   215	                        IconButton(
   216	                          icon: const Icon(Icons.paste_rounded, size: 20),
   217	                          tooltip: 'Paste from clipboard',
   218	                          onPressed: _onPasteRecipient,
   219	                        ),
   220	                        IconButton(
   221	                          icon: const Icon(Icons.qr_code_scanner_rounded, size: 20),
   222	                          tooltip: 'Scan QR Code',
   223	                          onPressed: _onScanQr,
   224	                        ),
   225	                      ],
   226	                    ),
   227	                  ),
   228	                ),
   229	                const SizedBox(height: 24),
   230	
   231	                // Amount Input
   232	                Row(
   233	                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
   234	                  children: [
   235	                    Text(
   236	                      'Amount',
   237	                      style: theme.textTheme.titleSmall?.copyWith(
   238	                        fontWeight: FontWeight.bold,
   239	                      ),
   240	                    ),
   241	                    TextButton(
   242	                      onPressed: () => _onSetMaxAmount(balance, fee),
   243	                      style: TextButton.styleFrom(
   244	                        padding: EdgeInsets.zero,
   245	                        minimumSize: const Size(40, 24),
   246	                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
   247	                      ),
   248	                      child: Text(
   249	                        'MAX',
   250	                        style: TextStyle(
   251	                          color: theme.colorScheme.primary,
   252	                          fontWeight: FontWeight.bold,
   253	                        ),
   254	                      ),
   255	                    ),
   256	                  ],
   257	                ),
   258	                const SizedBox(height: 8),
   259	                TextFormField(
   260	                  controller: _amountController,
   261	                  keyboardType:
   262	                      const TextInputType.numberWithOptions(decimal: true),
   263	                  inputFormatters: [
   264	                    FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d*')),
   265	                  ],
   266	                  style: theme.textTheme.titleMedium?.copyWith(
   267	                    fontWeight: FontWeight.bold,
   268	                  ),
   269	                  decoration: InputDecoration(
   270	                    hintText: '0.00',
   271	                    suffixIcon: Padding(
   272	                      padding: const EdgeInsets.symmetric(horizontal: 16),
   273	                      child: Column(
   274	                        mainAxisAlignment: MainAxisAlignment.center,
   275	                        children: [
   276	                          Text(
   277	                            'VRDX',
   278	                            style: theme.textTheme.titleSmall?.copyWith(
   279	                              color: theme.colorScheme.primary,
   280	                              fontWeight: FontWeight.bold,
   281	                            ),
   282	                          ),
   283	                        ],
   284	                      ),
   285	                    ),
   286	                  ),
   287	                ),
   288	                const SizedBox(height: 24),
   289	
   290	                // Fee Estimate Selector
   291	                FeeEstimateWidget(
   292	                  recipient: _recipientController.text,
   293	                  amount: currentAmount,
   294	                ),
   295	
   296	                const SizedBox(height: 32),
   297	
   298	                // Send Action Button
   299	                VerdisButton(
   300	                  label: 'Review Transfer',
   301	                  icon: Icons.arrow_forward_rounded,
   302	                  onPressed: _onSubmitSend,
   303	                ),
   304	              ],
   305	            ),
   306	          ),
   307	        ),
   308	      ),
   309	    );
   310	  }
   311	}
