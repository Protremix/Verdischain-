     1	import 'package:flutter/material.dart';
     2	
     3	/// Glassmorphism card displaying total VRDX balance, USD value, 24h change, and allocation breakdown on tap.
     4	class BalanceCard extends StatelessWidget {
     5	
     6	  const BalanceCard({
     7	    super.key,
     8	    required this.balance,
     9	    this.vrdxPriceUsd = 0.25,
    10	    this.change24hPercent = 5.4,
    11	    this.onTap,
    12	  });
    13	  final int balance; // In base units (10 decimals: 1 VRDX = 10,000,000,000)
    14	  final double vrdxPriceUsd;
    15	  final double change24hPercent;
    16	  final VoidCallback? onTap;
    17	
    18	  double get vrdxAmount => balance / 10000000000.0;
    19	  double get usdValue => vrdxAmount * vrdxPriceUsd;
    20	
    21	  void _showAllocationBreakdown(BuildContext context) {
    22	    final theme = Theme.of(context);
    23	
    24	    showModalBottomSheet(
    25	      context: context,
    26	      backgroundColor: theme.colorScheme.surface,
    27	      shape: const RoundedRectangleBorder(
    28	        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
    29	      ),
    30	      builder: (context) {
    31	        return Padding(
    32	          padding: const EdgeInsets.all(24.0),
    33	          child: Column(
    34	            mainAxisSize: MainAxisSize.min,
    35	            crossAxisAlignment: CrossAxisAlignment.start,
    36	            children: [
    37	              Center(
    38	                child: Container(
    39	                  width: 40,
    40	                  height: 4,
    41	                  decoration: BoxDecoration(
    42	                    color: theme.colorScheme.onSurfaceVariant.withOpacity(0.4),
    43	                    borderRadius: BorderRadius.circular(2),
    44	                  ),
    45	                ),
    46	              ),
    47	              const SizedBox(height: 20),
    48	              Text(
    49	                'Portfolio Allocation Breakdown',
    50	                style: theme.textTheme.headlineSmall?.copyWith(
    51	                  fontWeight: FontWeight.bold,
    52	                ),
    53	              ),
    54	              const SizedBox(height: 16),
    55	              _buildAllocationRow(
    56	                context,
    57	                title: 'Liquid VRDX',
    58	                amount: '${vrdxAmount.toStringAsFixed(2)} VRDX',
    59	                percentage: '44.7%',
    60	                color: theme.colorScheme.primary,
    61	              ),
    62	              const Divider(height: 24),
    63	              _buildAllocationRow(
    64	                context,
    65	                title: 'Staked VRDX (gVRDX)',
    66	                amount: '15,400.00 VRDX',
    67	                percentage: '55.3%',
    68	                color: const Color(0xFF00FF88),
    69	              ),
    70	              const Divider(height: 24),
    71	              _buildAllocationRow(
    72	                context,
    73	                title: 'Total Portfolio Value',
    74	                amount: '\$${(usdValue + (15400 * vrdxPriceUsd)).toStringAsFixed(2)} USD',
    75	                percentage: '100.0%',
    76	                color: Colors.white,
    77	                isBold: true,
    78	              ),
    79	              const SizedBox(height: 24),
    80	              SizedBox(
    81	                width: double.infinity,
    82	                child: ElevatedButton(
    83	                  onPressed: () => Navigator.pop(context),
    84	                  child: const Text('Close'),
    85	                ),
    86	              ),
    87	            ],
    88	          ),
    89	        );
    90	      },
    91	    );
    92	  }
    93	
    94	  Widget _buildAllocationRow(
    95	    BuildContext context, {
    96	    required String title,
    97	    required String amount,
    98	    required String percentage,
    99	    required Color color,
   100	    bool isBold = false,
   101	  }) {
   102	    final theme = Theme.of(context);
   103	    final textStyle = isBold
   104	        ? theme.textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.bold)
   105	        : theme.textTheme.bodyMedium;
   106	
   107	    return Row(
   108	      children: [
   109	        Container(
   110	          width: 12,
   111	          height: 12,
   112	          decoration: BoxDecoration(
   113	            color: color,
   114	            shape: BoxShape.circle,
   115	          ),
   116	        ),
   117	        const SizedBox(width: 12),
   118	        Expanded(
   119	          child: Text(title, style: textStyle),
   120	        ),
   121	        Column(
   122	          crossAxisAlignment: CrossAxisAlignment.end,
   123	          children: [
   124	            Text(amount, style: textStyle),
   125	            Text(
   126	              percentage,
   127	              style: theme.textTheme.labelSmall?.copyWith(
   128	                color: theme.colorScheme.onSurfaceVariant,
   129	              ),
   130	            ),
   131	          ],
   132	        ),
   133	      ],
   134	    );
   135	  }
   136	
   137	  @override
   138	  Widget build(BuildContext context) {
   139	    final theme = Theme.of(context);
   140	    final isPositive = change24hPercent >= 0;
   141	
   142	    return Card(
   143	      elevation: 0,
   144	      shape: RoundedRectangleBorder(
   145	        borderRadius: BorderRadius.circular(20),
   146	        side: BorderSide(
   147	          color: theme.colorScheme.primary.withOpacity(0.25),
   148	          width: 1.5,
   149	        ),
   150	      ),
   151	      child: InkWell(
   152	        onTap: onTap ?? () => _showAllocationBreakdown(context),
   153	        borderRadius: BorderRadius.circular(20),
   154	        child: Container(
   155	          decoration: BoxDecoration(
   156	            borderRadius: BorderRadius.circular(20),
   157	            gradient: LinearGradient(
   158	              colors: [
   159	                theme.colorScheme.surface,
   160	                theme.colorScheme.surfaceContainerHighest.withOpacity(0.8),
   161	                theme.colorScheme.primary.withOpacity(0.08),
   162	              ],
   163	              begin: Alignment.topLeft,
   164	              end: Alignment.bottomRight,
   165	            ),
   166	          ),
   167	          padding: const EdgeInsets.all(20.0),
   168	          child: Column(
   169	            crossAxisAlignment: CrossAxisAlignment.start,
   170	            children: [
   171	              Row(
   172	                mainAxisAlignment: MainAxisAlignment.spaceBetween,
   173	                children: [
   174	                  Row(
   175	                    children: [
   176	                      Container(
   177	                        padding: const EdgeInsets.all(6),
   178	                        decoration: BoxDecoration(
   179	                          color: theme.colorScheme.primary.withOpacity(0.15),
   180	                          shape: BoxShape.circle,
   181	                        ),
   182	                        child: Icon(
   183	                          Icons.account_balance_wallet,
   184	                          size: 16,
   185	                          color: theme.colorScheme.primary,
   186	                        ),
   187	                      ),
   188	                      const SizedBox(width: 8),
   189	                      Text(
   190	                        'Total Balance',
   191	                        style: theme.textTheme.labelLarge?.copyWith(
   192	                          color: theme.colorScheme.onSurfaceVariant,
   193	                        ),
   194	                      ),
   195	                    ],
   196	                  ),
   197	                  Container(
   198	                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
   199	                    decoration: BoxDecoration(
   200	                      color: (isPositive ? const Color(0xFF00E676) : theme.colorScheme.error)
   201	                          .withOpacity(0.15),
   202	                      borderRadius: BorderRadius.circular(12),
   203	                    ),
   204	                    child: Row(
   205	                      mainAxisSize: MainAxisSize.min,
   206	                      children: [
   207	                        Icon(
   208	                          isPositive ? Icons.trending_up : Icons.trending_down,
   209	                          size: 14,
   210	                          color: isPositive ? const Color(0xFF00E676) : theme.colorScheme.error,
   211	                        ),
   212	                        const SizedBox(width: 4),
   213	                        Text(
   214	                          '${isPositive ? '+' : ''}${change24hPercent.toStringAsFixed(1)}%',
   215	                          style: theme.textTheme.labelSmall?.copyWith(
   216	                            color: isPositive ? const Color(0xFF00E676) : theme.colorScheme.error,
   217	                            fontWeight: FontWeight.bold,
   218	                          ),
   219	                        ),
   220	                      ],
   221	                    ),
   222	                  ),
   223	                ],
   224	              ),
   225	              const SizedBox(height: 12),
   226	              Row(
   227	                crossAxisAlignment: CrossAxisAlignment.baseline,
   228	                textBaseline: TextBaseline.alphabetic,
   229	                children: [
   230	                  Text(
   231	                    vrdxAmount.toStringAsFixed(2),
   232	                    style: theme.textTheme.displayMedium?.copyWith(
   233	                      fontWeight: FontWeight.w800,
   234	                      letterSpacing: -0.5,
   235	                    ),
   236	                  ),
   237	                  const SizedBox(width: 8),
   238	                  Text(
   239	                    'VRDX',
   240	                    style: theme.textTheme.headlineSmall?.copyWith(
   241	                      color: theme.colorScheme.primary,
   242	                      fontWeight: FontWeight.bold,
   243	                    ),
   244	                  ),
   245	                ],
   246	              ),
   247	              const SizedBox(height: 6),
   248	              Row(
   249	                mainAxisAlignment: MainAxisAlignment.spaceBetween,
   250	                children: [
   251	                  Text(
   252	                    '≈ \$${usdValue.toStringAsFixed(2)} USD',
   253	                    style: theme.textTheme.titleMedium?.copyWith(
   254	                      color: theme.colorScheme.onSurfaceVariant,
   255	                    ),
   256	                  ),
   257	                  Row(
   258	                    children: [
   259	                      Text(
   260	                        'Tap for breakdown',
   261	                        style: theme.textTheme.labelSmall?.copyWith(
   262	                          color: theme.colorScheme.primary,
   263	                        ),
   264	                      ),
   265	                      const SizedBox(width: 4),
   266	                      Icon(
   267	                        Icons.chevron_right,
   268	                        size: 14,
   269	                        color: theme.colorScheme.primary,
   270	                      ),
   271	                    ],
   272	                  ),
   273	                ],
   274	              ),
   275	            ],
   276	          ),
   277	        ),
   278	      ),
   279	    );
   280	  }
   281	}
