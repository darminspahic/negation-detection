<?php

interface SimplifierInterface {
	
	function simplify( $outputFile );
	
}


class Simplifier implements SimplifierInterface {
	
	private $_inputFile = null;
	private $_outputFile = null;
	
	
	private function setOutputFile( $outputFile ) {
		if( basename($outputFile) == $outputFile ) {
			$outputFile = dirname( $this->_inputFile ) .'/'. $outputFile;
		}
		$this->_outputFile = $outputFile;
	}
	
	
	public function __construct( $inputFile ) {
		$this->_inputFile = $inputFile;
	}
	
	
	private static function getTerminalById( $sentence, $terminalId ) {
		foreach( $sentence->graph->terminals->t as $terminal ) {
			$attributes = current( $terminal->attributes() );
			if( $attributes['id'] == $terminalId )
				return $terminal;
		}
		return null;
	}
	
	
	private static function isNegatedSentence( $sentence ) {
		$frames = self::getNegationFrames( $sentence );
		foreach( $frames as $frame ) {
			if( $frame ) {
				$attributes = current( $frame->attributes() );
				if( strpos( strtolower( $attributes['name'] ), "negation" ) !== false )
					return true;
			}
		}
		return false;
	}
	
	
	private static function getNegationFrames( $sentence ) {
		$negationFrames = array();
		foreach( $sentence->sem->frames as $frames ) {
			foreach( $frames as $frame ) {
				$attributes = current( $frame->attributes() );
				if( strpos( strtolower( $attributes['name'] ), "negation" ) !== false )
					$negationFrames[] = $frame;
			}
		}
		return $negationFrames;
	}
	
	
	private static function getNegationTargets( $sentence ) {
		$targets = array();
		$frames = self::getNegationFrames( $sentence );
		foreach( $frames as $frame ) {
			if( $frame ) {
				$attributes = current( $frame->attributes() );
				$targets[ $attributes['id'] ] = $frame->target;
			}
		}
		return $targets;
	}
	
	
	private static function getNegationFocuses( $sentence ) {
		$focuses = array();
		$frames = self::getNegationFrames( $sentence );
		foreach( $frames as $frame ) {
			if( $frame ) {
				$frameAttributes = current( $frame->attributes() );
				foreach( $frame->fe as $fe ) {
					$attributes = $fe->attributes();
					if( strpos( strtolower( $attributes['name'] ), "focus" ) !== false ) {
						$fe->addAttribute( 'frameId', $frameAttributes['id'] );
						$focuses[] = $fe;
					}
				}
			}
		}
		return $focuses;
	}
	
	
	private static function getNegationScopes( $sentence ) {
		$scopes = array();
		$frames = self::getNegationFrames( $sentence );
		foreach( $frames as $frame ) {
			if( $frame ) {
				$frameAttributes = current( $frame->attributes() );
				foreach( $frame->fe as $fe ) {
					$attributes = $fe->attributes();
					if( strpos( strtolower( $attributes['name'] ), "scope" ) !== false ) {
						$fe->addAttribute( 'frameId', $frameAttributes['id'] );
						$scopes[] = $fe;
					}
				}
			}
		}
		return $scopes;
	}
	
	
	private static function getNegatedTerminals( $sentence, $sort=true ) {
		$terminals = array();
		$negationTargets = self::getNegationTargets( $sentence );
		foreach( $negationTargets as $frameId => $negationTarget ) {
			foreach( $negationTarget->fenode as $fenode ) {
				$attributes = $fenode->attributes();
				$idref = current( $attributes['idref'] );
				$terminal = self::getTerminalById( $sentence, $idref );
				if( $terminal ) {
					$terminal->addAttribute( 'frameId', $frameId );
					if( $sort )
						$terminals[ $idref ] = $terminal;
					else
						$terminals[] = $terminal;
				}
			}
		}
		if( $sort )
			ksort( $terminals );
		return $terminals;
	}
	
	
	private static function getNegationFocusTerminals( $sentence, $sort=true ) {
		$terminals = array();
		$negationFocuses = self::getNegationFocuses( $sentence );
		foreach( $negationFocuses as $negationFocus ) {
			$focusAttributes = current( $negationFocus->attributes() );
			$frameId = $focusAttributes['frameId'];
			foreach( $negationFocus->fenode as $fenode ) {
				$attributes = $fenode->attributes();
				$idref = current( $attributes['idref'] );
				$terminal = self::getTerminalById( $sentence, $idref );
				if( $terminal ) {
					@$terminal->addAttribute( 'frameId', $frameId );
					if( $sort )
						$terminals[ $idref ] = $terminal;
					else
						$terminals[] = $terminal;
				}
			}
		}
		if( $sort )
			ksort( $terminals );
		return $terminals;
	}
	
	
	private static function getNegationScopeTerminals( $sentence, $sort=true ) {
		$terminals = array();
		$negationScopes = self::getNegationScopes( $sentence );
		foreach( $negationScopes as $negationScope ) {
			$scopeAttributes = current( $negationScope->attributes() );
			$frameId = $scopeAttributes['frameId'];
			foreach( $negationScope->fenode as $fenode ) {
				$attributes = $fenode->attributes();
				$idref = current( $attributes['idref'] );
				$terminal = self::getTerminalById( $sentence, $idref );
				if( $terminal ) {
					@$terminal->addAttribute( 'frameId', $frameId );
					if( $sort )
						$terminals[ $idref ] = $terminal;
					else
						$terminals[] = $terminal;
				}
			}
		}
		if( $sort )
			ksort( $terminals );
		return $terminals;
	}
	
	
	private static function getFrameId( $terminal, $terminalSet ) {
		foreach( $terminalSet as $key => $curTerminal ) {
			if( $terminal == $curTerminal && is_object($terminal) ) {
				$attributes = $terminal->attributes();
				return $attributes['frameId'];
			}
		}
		return "";
	}
	
	
	public function simplify( $outputFile ) {
		$this->setOutputFile( $outputFile );
		
		$XML = simplexml_load_file( $this->_inputFile );
		
		$simplifiedSentences = $this->simplifySentences( current( $XML->body ) );
		
		file_put_contents( $this->_outputFile, $simplifiedSentences );
	}
	
	
	private function simplifySentences( $sentences, $negationMarkup=true ) {
		$simplifiedSentences = array();
		$j = 0;
		foreach( $sentences as $i => $sentence ) {
			if( !self::isNegatedSentence( $sentence ) )
				continue; // Sätze ohne Verneinung überspringen
			$prevSentence = $sentences[ $i-1 ];
			$nextSentence = $sentences[ $i+1 ];
		#	if( $j == 32 ) {
				$simplifiedSentences[] = $this->simplifySentence( $sentence, $prevSentence, $nextSentence, $negationMarkup );
		#		echo current($simplifiedSentences); exit;
		#	}
			$j++;
		}
		
		if( $negationMarkup )
			$simplifiedSentences = "<sentences>\n". '<sentence>'. implode( "</sentence>\n<sentence>", $simplifiedSentences ) .'</sentence>' ."\n</sentences>";
		else
			$simplifiedSentences = implode( "\n", $simplifiedSentences );
						
		return $simplifiedSentences;
	}
	
	
	private function simplifySentence( $sentence, $prevSentence=null, $nextSentence=null, $negationMarkup=true ) {
		$negatedTerminals = self::getNegatedTerminals( $sentence );
		$scope = self::getNegationScopeTerminals( $sentence );
		$focus = self::getNegationFocusTerminals( $sentence );
		
		$joinedSentence = '';
		$terminals = current( $sentence->graph->terminals );
		$openMarkupTags = array();
		foreach( $terminals as $terminal ) {
			$attributes = current( $terminal->attributes() );
						
			if( $negationMarkup ) {
				if( !in_array( $terminal, $negatedTerminals ) && array_key_exists( 'negation', $openMarkupTags ) ) {
					$joinedSentence .= '</negation>';
					unset( $openMarkupTags['negation'] );
				}
				if( !in_array( $terminal, $focus ) && array_key_exists( 'focus', $openMarkupTags ) ) {
					$joinedSentence .= '</focus>';
					unset( $openMarkupTags['focus'] );
				}
				if( !in_array( $terminal, $scope ) && array_key_exists( 'scope', $openMarkupTags ) ) {
					$joinedSentence .= '</scope>';
					unset( $openMarkupTags['scope'] );
				}
			}
			
			if( substr( $attributes['pos'], 0, 1 ) !== '$' )
				$joinedSentence .= ' ';
			
			if( $negationMarkup ) {
				if( in_array( $terminal, $scope ) && !array_key_exists( 'scope', $openMarkupTags ) ) {
					$joinedSentence .= '<scope frame="'. self::getFrameId($terminal, $scope) .'">';
					$openMarkupTags['scope'] = true;
				}
				if( in_array( $terminal, $focus ) && !array_key_exists( 'focus', $openMarkupTags ) ) {
					$joinedSentence .= '<focus frame="'. self::getFrameId($terminal, $focus) .'">';
					$openMarkupTags['focus'] = true;
				}
				if( in_array( $terminal, $negatedTerminals ) && !array_key_exists( 'negation', $openMarkupTags ) ) {
					$joinedSentence .= '<negation frame="'. self::getFrameId($terminal, $negatedTerminals) .'">';
					$openMarkupTags['negation'] = true;
				}
			}
			
			$joinedSentence .= $attributes['word'];
		}
		$joinedSentence = trim( $joinedSentence );
		
		return $joinedSentence;
	}
	
}


class DirectorySimplifier {
	
	private $_inputDirectory = null;
	private $_outputDirectory = null;
	private $_resursive = false;
	private $_suffixInsertion = 'simplified';
	
	
	public function __construct( $inputDirectory, $outputDirectory=null, $recursive=false ) {
		$this->_inputDirectory = $inputDirectory;
		$this->_outputDirectory = $outputDirectory !== null ? $outputDirectory : $inputDirectory;
		$this->_resursive = $recursive ? true : false;
	}
	
	
	public function simplify() {
		foreach( scandir( $this->_inputDirectory ) as $directoryChild ) {
			$suffix = array_pop( explode( '.', $directoryChild ) );
			$file = $this->_inputDirectory .'/'. $directoryChild;
			$simplifiedFile = $this->_outputDirectory .'/'. str_replace( '.'. $suffix, '.'. $this->_suffixInsertion .'.'. $suffix, $directoryChild );
			if( substr( $directoryChild, 0, 1 ) == '.' || strpos( $file, '.'. $this->_suffixInsertion .'.' ) !== false )
				continue;
			if( !is_file( $file ) ) {
				if( $this->_resursive && is_dir( $file ) ) {
					$DirSimplifier = new DirectorySimplifier( $file, $this->_inputDirectory == $this->_outputDirectory ? $file : $this->_outputDirectory, $this->_resursive );
					$DirSimplifier->simplify();
				}
				continue;
			}
			$Simplifier = new Simplifier( $file );
			$Simplifier->simplify( $simplifiedFile );
		}
	}
	
	
}


/*
 *	USAGE
 */

$Simplifier = new DirectorySimplifier( '../../data/xml/', null, true );
$Simplifier->simplify();