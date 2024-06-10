cmake_minimum_required(VERSION 2.6)
PROJECT(  llama_agent )

INCLUDE( /home/robocomp/robocomp/cmake/robocomp.cmake )

ROBOCOMP_IDSL_TO_ICE( CommonBehavior LLM )
